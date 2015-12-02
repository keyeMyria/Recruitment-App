from models import EveCharacter, EveAllianceInfo, EveApiKeyPair, EveCorporationInfo
from models import User, Role, roles_users
from flask_security import current_user
from recruit_app.admin import AuthenticatedModelView
from wtforms import PasswordField
from recruit_app.recruit.models import HrApplication, HrApplicationComment
from recruit_app.blacklist.models import BlacklistCharacter

def register_admin_views(admin, db):
    admin.add_view(EveCharacterAdmin(EveCharacter, db.session, category='EvE'))
    admin.add_view(EveCorporationInfoAdmin(EveCorporationInfo, db.session, category='EvE'))
    admin.add_view(EveAllianceInfoAdmin(EveAllianceInfo, db.session, category='EvE'))
    admin.add_view(EveApiKeyPairAdmin(EveApiKeyPair, db.session, category='EvE'))
    admin.add_view(UserAdmin(User, db.session, endpoint="users", category='Users'))
    admin.add_view(RoleAdmin(Role, db.session, category='Users'))

# Useful things: column_list, column_labels, column_searchable_list, column_filters, form_columns, form_ajax_refs

class EveCharacterAdmin(AuthenticatedModelView):
    column_list = (
        'character_id',
        'character_name',
        'corporation.corporation_name',
        'alliance.alliance_name',
        'user.email',
        'api.api_id', )
    column_labels = {
        'corporation.corporation_name': 'Corp',
        'alliance.alliance_name':       'Alliance',
        'user.email':                   'User Email',
        'api.api_id':                   'API', }
    column_searchable_list = column_list
    column_filters = column_list
    form_columns = ('character_id',
        'character_name',
        'corporation',
        'alliance',
        'user',
        'api' )
    form_ajax_refs = {
        'corporation': { 'fields': ('corporation_name',) },
        'alliance':    { 'fields': ('alliance_name',) },
        'user':        { 'fields': (User.email,) },
        'api':         { 'fields': (EveApiKeyPair.api_id,) } }

class EveCorporationInfoAdmin(AuthenticatedModelView):
    column_list = (
        'corporation_id',
        'corporation_name',
        'corporation_ticker',
        'alliance.alliance_name',
        'member_count',
        'is_blue', )
    column_labels = {
        'corporation_id': 'ID',
        'corporation_name': 'Name',
        'corporation_ticker': 'Ticker',
        'alliance.alliance_name' : 'Alliance', }
    column_searchable_list = (
        'corporation_name',
        'corporation_ticker',
        'alliance.alliance_name', )
    column_filters = column_list
    form_columns = (
        'corporation_id',
        'corporation_name',
        'corporation_ticker',
        'alliance',
        'member_count',
        'is_blue', )
    form_ajax_refs = {
        'alliance': { 'fields': ('alliance_name', ) }, }

class EveAllianceInfoAdmin(AuthenticatedModelView):
    column_list = (
        'alliance_id',
        'alliance_name',
        'alliance_ticker',
        'executor_corp_id',
        'member_count',
        'is_blue', )
    column_searchable_list = (
        'alliance_name',
        'alliance_ticker', )
    column_filters = column_list
    form_columns = column_list

class UserAdmin(AuthenticatedModelView):
    column_searchable_list = (
        'email',
        'last_login_ip',
        'current_login_ip',
        'main_character.character_name', )
    column_labels = {
        'main_character.character_name': 'Main', }
    column_list = (
        'email',
        'main_character.character_name',
        'created_at',
        'last_login_at',
        'confirmed_at',
        'active',
        'login_count',
        'last_login_ip',
        'current_login_ip', )
    column_filters = column_list
    form_columns = (
        'email',
        'password',
        'active',
        'is_admin',
        'created_at',
        'confirmed_at',
        'last_login_at',
        'current_login_at',
        'last_login_ip',
        'current_login_ip',
        'login_count',
        'roles',
        'characters',
        'api_keys',
        'blacklist_character_entries', )
    form_extra_fields = { 'password': PasswordField('Password') }    
    form_ajax_refs = {
        'characters':                  { 'fields': (EveCharacter.character_name, ) },
        'api_keys':                    { 'fields': (EveApiKeyPair.api_id, ) },
        'blacklist_character_entries': { 'fields': (BlacklistCharacter.name, BlacklistCharacter.notes, ) }, }

class RoleAdmin(AuthenticatedModelView):
    column_searchable_list = ('name', 'description')
    column_filters = column_searchable_list
    form_columns = ('id', ) + column_searchable_list + ('users', )
    form_ajax_refs = { 'users': { 'fields': ( User.email, ) } }

class EveApiKeyPairAdmin(AuthenticatedModelView):
    # TODO Would be nice to have main in here once it's one-to-one
    column_searchable_list = (
        'api_id',
        'api_key',
        'user.email',
        'user.main_character.character_name', )
    column_list = column_searchable_list + (
        'last_update_time',
        'valid')
    column_labels = {
        'user.email': 'User',
        'user.main_character.character_name': 'Main', }
    column_filters = column_list
    form_columns = (
        'api_id',
        'api_key',
        'last_update_time',
        'valid',
        'user',
        'characters', )
    form_ajax_refs = {
        'user':       { 'fields': ( User.email, ) },
        'characters': { 'fields': ( EveCharacter.character_name, ) }, }

def check_if_admin():
    if current_user:
        if current_user.has_role("admin"):
            return True
        else:
            return False
    else:
        return False
