from cgi import test
from operator import index

from sqlalchemy import func
from vpi_teams_bot import VpiSkKernel2
import pandas as pd
from pandasai import PandasAI
from pandasai.llm import OpenAI
import os

llm = OpenAI(os.getenv(key='OPENAI_API_KEY'))
pd_ai = PandasAI(llm, enable_cache= False)

kernel = VpiSkKernel2()

from vpi_bot_skills.chatSkills.memorySearch import TextMemorySkill


# df = pd.read_csv('./data/diemthi2019.csv')

# function1 = kernel.get_semantic_skill('databaseSkills')['getPythonCode']
# test_context = kernel.get_context('test')
# question = 'tìm 10 sbd có điểm toán cao nhất'
# test_context['input'] = question
# test_context['df_head'] = df.head().to_csv(index= False)
# test_context['num_rows'] = str(df.shape[0])
# test_context['num_columns'] = str(df.shape[1])

# print(df.head())

# check = function1.invoke(context = test_context)
# print(check)

# check_pd = pd_ai(df, question)
# print(check_pd)

test_context = kernel.get_context('chat')
func2 = kernel.import_skill(TextMemorySkill())['recall']
test_context['input'] = 'nhà máy lọc dầu đầu tiên của Việt Nam'
res = func2.invoke(context= test_context)
print(res)