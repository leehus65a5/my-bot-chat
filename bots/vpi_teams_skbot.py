# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json

from typing import List
from botbuilder.core import CardFactory, TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters, Attachment, Activity
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from botbuilder.schema._connector_client_enums import ActionTypes
from semantic_kernel import Kernel
from vpi_teams_bot.vpi_sk_config import VpiSkKernel
from semantic_kernel import SKContext
from vpi_teams_bot.vpi_sk_context import VpiSkContext
from vpi_teams_bot.vpi_sk_config2 import VpiSkKernel2
from vpi_bot_skills.chatSkills.memorySearch import TextMemorySkill
from vpi_bot_skills.native_skills.chat_authen_skills import AuthenChatUser
from vpi_bot_skills.native_skills.chat_database_skills import ChatWithDataBase
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class VpiBot(TeamsActivityHandler):
    
    SCHEMAS = """
    Table: students
    Collumns:
        - id: id 
        - name: student's name
        - birthday: student's birthday
        - address: adress

    Table: grades
    Collumns:
        - id : id
        - studentid: student's id in students table
        - courseid: course's id in cousrse table
        - score: score of stundet id learning this course id

    Table: courses
    Collumns:
        - id: id
        - courseName: name of course 
            - courseName value: ['Toán','Vật Lý','Hóa']
        - lecturer: name of teacher teach this course
    """
    # Vpi_Kernel = VpiSkKernel()
    Vpi_Kernel = VpiSkKernel2()
    
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password
        # self._kernel = VpiBot.Vpi_Kernel.get_kernel()
        self._kernel = VpiBot.Vpi_Kernel
        self._chat_history = self._kernel.get_context('history')
        self._db_context = self._kernel.get_context('query')
        # self._connector = create_engine('mysql://root:''@localhost/student').connect()

    async def on_teams_members_added(  # pylint: disable=unused-argument
        self,
        teams_members_added: list[TeamsChannelAccount],
        team_info: TeamInfo,
        turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome to the team { member.given_name } { member.surname }. "
                )

    async def on_message_activity(self, turn_context: TurnContext):
        TurnContext.remove_recipient_mention(turn_context.activity)
        text = turn_context.activity.text.strip().lower()

        if "check" in text:
            # get_role = self._kernel.import_skill(AuthenChatUser(),'authenUser')['authen']
            # check_context = self._kernel.get_context('check')
            # check_context['turn_context'] = turn_context
            # await get_role.invoke_async(context= check_context)
            # print(check_context.result)
            # member = await TeamsInfo.get_member(turn_context, turn_context.activity.from_property.id)
            # print(member)
            # print('member mail', member.email)
            await turn_context.send_activity(f'check ok')
            return

        if 'qna' in text:
            await self._qna_activity(turn_context, text)
            return
        
        if 'db1' in text:
            text = " ".join(text.strip().split()[1:]) if len(text.strip()) > 2 else 'hello db'
            db_context = self._db_context
            db_context['data_objective'] = text
            db_context['data_schemas'] = VpiBot.SCHEMAS
            await self._chat_database(turn_context= turn_context, context= db_context)
            await turn_context.send_activity('end database')
            return 

        if 'db' in text:
            db_context = self._kernel.get_context('db_question')
            text = " ".join(text.strip().split()[1:]) if len(text.strip()) > 2 else 'hello db'
            db_context.put(text)
            out = str(db_context['db_question'])
            await turn_context.send_activity(MessageFactory.text('db test ' + out))
            return
        
        # chat_context = self._kernel.get_context('history') 
        chat_context = self._chat_history
        chat_context['user_input']  = text
        await self._chat(turn_context,context= chat_context)
        return

    async def _qna_activity(self, turn_context: TurnContext, question_in: str):
        text = question_in.strip().split()
        question = " ".join(text[1:]) if len(text) > 1 else " ".join(text)  # bug
        results = await self._kernel.memory.search_async("history-pvn", query=question, limit=1)
        
        if results[0].relevance < 0.85:
            await turn_context.send_activity(
                MessageFactory.text("<span style='color: red; font-weight: bold;'>QnA: </span> Không tìm thấy dữ liệu có điểm score phù hợp (> 0.85)"))
            return
        
        await turn_context.send_activity(
            MessageFactory.text(f"<span style='color: red; font-weight: bold;'>QnA: </span> {results[0].text} <br><br><strong>Relevance</strong>: {results[0].relevance}"))
    
    async def _chat(self, turn_context: TurnContext, context: VpiSkContext):
        
        basicChat = self._kernel.get_semantic_skill('chatSkills')['basicChat']
        classication = self._kernel.get_semantic_skill('chatSkills')['classfication']
        get_memory_id = self._kernel.get_semantic_skill('chatSkills')['getMemoryId']
        textSkill = self._kernel.import_skill(TextMemorySkill())
        memorySearch = textSkill['recall']
        memoryUpdate = textSkill['save']
        authen = self._kernel.import_skill(AuthenChatUser())['authen']
        
        await classication.invoke_async(context = context)
        get_cls = json.loads(context.result)
        
        if get_cls['type'] == 'question':
            history = f"\nUser: {context['user_input']}\n" 
            re = await memorySearch.invoke_async(context= context)
            if re['input']:
                ans, rel, id = json.loads(re.result)['result'], json.loads(re.result)['relevance'], json.loads(re.result)['id']
                history += f'\nMemory text: {ans}\nMemory relevance: {rel}\nMemory id: {id}\n'
                context.put(history)
                await turn_context.send_activity(MessageFactory.text(f"<span style='color: red; font-weight: bold;'>Memory: </span> {ans} <br><br><strong>Relevance</strong>: {rel}")) 
                return
            result = await basicChat.invoke_async(context=context)
            history += f'\nVPI-BotChat: {result}\n'
            context.put(history)
            await turn_context.send_activity(MessageFactory.text(f"<span style='color: red; font-weight: bold;'>VPI-ChatBot: </span> {str(result)}"))
        else:
            context['user_input'] = get_cls['value']
            await get_memory_id.invoke_async(context=context)
            print(context.get())
            keys = str(context.result).strip()
            if keys == 'False':
                await turn_context.send_activity(MessageFactory.text('not found information need to update!!!'))
                return
            context['turn_context'] = turn_context
            await authen.invoke_async(context = context)
            role = context.result.strip()
            print('role = ', role, role != 'admin')
            if role != 'admin':
                await turn_context.send_activity(MessageFactory.text('User dont have permession to update memory'))
                return
            context['key'] = keys 
            await memoryUpdate.invoke_async(get_cls['value'], context = context)
            await turn_context.send_activity(MessageFactory.text("<span style='color: red; font-weight: bold;'>Update-Session: </span>" + get_cls['value']))
    
    async def _chat_database(self, turn_context: TurnContext, context : VpiSkContext):
        sql_generate = self._kernel.get_semantic_skill('databaseSkills')['genSqlQuery']
        exec_query = self._kernel.import_skill(ChatWithDataBase())['execute']
        await sql_generate.invoke_async(context = context)
        query = self._sql_helper(context.result.strip())
        context['query'] = query
        await turn_context.send_activity(MessageFactory.text(f"<span style='color: red; font-weight: bold;'>SQL_QUERY: </span> {str(query)}"))
        await exec_query.invoke_async(context= context)
        result = str(context.result)
        await turn_context.send_activity(MessageFactory.text(f"<span style='color: red; font-weight: bold;'>SQL_RESULT: </span> {str(result)}"))

    def _sql_helper(self, sql_query: str) -> str:
        if not sql_query:
            return None
        sql_query = sql_query[sql_query.find(':') + 1:] if 'Answer' in sql_query else sql_query
        return sql_query
    
    