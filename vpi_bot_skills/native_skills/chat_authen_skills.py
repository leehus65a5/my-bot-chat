from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel import SKContext
from semantic_kernel.sk_pydantic import PydanticField
from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsInfo
from vpi_teams_bot import VpiSkKernel2

class AuthenChatUser(PydanticField):
	_admin = ['admin1', 'toanln@vpitraining.onmicrosoft.com']
	_user = ['user1','bot2@ai4oilgas.onmicrosoft.com']
 
	@sk_function(
		description='get role of the user',
		name='authen',
	)
	async def get_auth(self, context:SKContext) -> str:
		print('----------------------get authen------------------------')
		turn_context = context['turn_context']
		member = await TeamsInfo.get_member(turn_context, turn_context.activity.from_property.id)
		member_mail = member.email
		user_role =  'user' if member_mail in AuthenChatUser._user else 'admin' if member_mail in AuthenChatUser._admin else ''
		return user_role