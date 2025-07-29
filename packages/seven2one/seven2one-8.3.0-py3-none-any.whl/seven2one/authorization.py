from typing import Optional
from uuid import uuid4
import pandas as pd
from loguru import logger

from .utils.ut_graphql import GraphQLUtil
from .utils.ut_error_handler import ErrorHandler

from seven2one.core_interface import ITechStack
from seven2one.dynamicobjects_interface import IDynamicObjects

class Authorization:

    def __init__(self, endpoint: str, techStack: ITechStack, dynamicObjects: IDynamicObjects) -> None:
        self.techStack = techStack
        self.endpoint = endpoint
        self.dynamicObjects = dynamicObjects

    def getVersion(self):
        """
        Returns name and version of the responsible micro service
        """

        return GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'authorization')

    def _resolve_where(self, where: Optional[str]):
        resolvedFilter = ''
        if where != None: 
            resolvedFilter = f'({GraphQLUtil.resolve_where_dyno(self.techStack, self.dynamicObjects, where)["topLevel"]})'
        
        return resolvedFilter

    def roles(self, nameFilter: Optional[str] = None) -> pd.DataFrame:
        """
        Returns a DataFrame of available roles.

        Parameters:
        -----------
        nameFilter : str, optional
            Filters the roles by role name.
        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with name, id and revision of the role.
        """
        key = 'roles'

        _fields = '''
            id
            name
            revision
        '''

        where_string = "" 
        if nameFilter is not None:
            where_string = f'(where:{{name:{{eq:"{nameFilter}"}}}})'

        graphQLString = f'''query roles {{
            {key} {where_string}
            {{ 
                {_fields}
            }}
        }}'''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if (not isinstance(result, dict)):
            return pd.DataFrame()
        
        df = pd.json_normalize(result[key])

        return df

    def rules(
        self,
        fields:Optional[list]=None, 
        where:Optional[str]=None
        ) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame of available rules
        """

        key = 'rules'

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields =f'''
                id
                filter
                revision
                role {{
                    id
                    name
                }}
                accountReference {{
                    ...on GroupReference {{
                        group {{
                            id
                            name
                        }}
                    }}
                    ...on ServiceAccountReference {{
                        serviceAccount {{
                            id
                            name
                        }}
                    }}
                }}
            ''' 

        resolvedFilter = self._resolve_where(where)
        graphQLString = f'''query Rules {{
            {key}{resolvedFilter}  {{
                {_fields}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif not isinstance(result, dict):
            raise Exception("Result is not a dictionary")
        
        df = pd.json_normalize(result[key])
        return df
    
    def addUsers(self, provider_user_ids: list, fields: Optional[list] = None) -> Optional[pd.DataFrame]:
        """
        Adds a list of users from Authentik via the provider_users_id to the Authorization-Service users list and returns a data frame with user information.
        Fields defines the values that are returned. By default id, providerSubject, providerUserId and userId are returned.

        Parameters:
        -----------
        provider_user_ids : list
            A list of provider user IDs to add.
        fields: list, optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user information (Default: id, providerSubject, providerUserId, userId).
        """

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields =f'''
                id
                providerSubject
                providerUserId
                userId
            ''' 

        correlation_id = str(uuid4())
        with logger.contextualize(correlation_id = correlation_id):
            key = 'addUsers'
            graphQLString = f'''mutation {key} {{
                {key}(input: {{
                    providerUserIds: ["{'", "'.join(provider_user_ids)}"]
                }}) {{
                    users {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if result is None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result[key]['users'])
            return df
        

    
    def addUsersToGroups(self, user_ids: list, group_ids: list, fields: Optional[list] =  None) -> pd.DataFrame:
        """
        Adds one or more users to one or more groups and returns a pandas DataFrame with user information.
        Fields defines the values that are returned. By default userId and groupIds are returned.

        Parameters:
        -----------
        user_ids : list
            A list of user IDs to add to the groups.
        group_ids : list
            A list of group IDs to add the users to.
        fields : list, optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user and group information (Default:userId, groupIds).
        """
        correlation_id = str(uuid4())

        if fields is not None:
            if not isinstance(fields, list):
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            _fields = '''
                userId
                groupIds
            '''

        with logger.contextualize(correlation_id=correlation_id):
            key = 'addUsersToGroups'

            user_inputs = []
            for user_id in user_ids:
                for group_id in group_ids:
                    user_inputs.append(f'{{ userId: "{user_id}", groupIds: "{group_id}" }}')
            user_inputs_str = ', '.join(user_inputs)

            graphQLString = f'''mutation {{
                {key}(input: {{users: [{user_inputs_str}], }}) {{
                    users {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if result is None:
                return pd.DataFrame()
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            users = result[key]['users']
            df = pd.DataFrame(users)

        return df

    def getAvailableUsers(self, usernames: Optional[list] = None, fields: Optional[list] = None ) -> pd.DataFrame:
        """
        Retrieves available users, including all Users in Authentik, and returns a list with user information. Users can be filtered via the 'usernames' parameter.
        Fields defines the values that are returned. By default providerUserId, eMail and username are returned.
        The username will always be returned.

        Parameters:
        -----------
        usernames : list, optional
            A list of usernames to filter the results by.
        fields : list, optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user and group information (Default:providerUserId, eMail).
        """

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields =f'''
                providerUserId
                eMail
            ''' 

        correlation_id = str(uuid4())

        with logger.contextualize(correlation_id=correlation_id):
            key = 'availableUsers'
            graphQLString = f'''query {key} {{
                {key} {{
                    username
                    {_fields}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if not isinstance(result, dict):
                return pd.DataFrame()

            users = result[key]

            filtered_users = []
            if usernames is not None:
                filtered_users = []
                for user in users:
                    if user['username'] in usernames:
                        filtered_users.append(user)
            users = filtered_users

            df = pd.json_normalize(users)

            return df
        
  
    def addGroups(self, group_names: list, fields: Optional[list] = None) -> pd.DataFrame:
        """
        Adds a list of groups and returns a pandas DataFrame with group information.
        Fields defines the values that are returned. By default name and id are returned

        Parameters:
        -----------
        group_names : list
            A list of group names to add.
        fields : list, optional
            A list of fields to include in the results. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with group information (Default:name, id).
        """
        if fields is not None:
            if not isinstance(fields, list):
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            _fields = '''
                name
                id
            '''

        correlation_id = str(uuid4())

        with logger.contextualize(correlation_id=correlation_id):
            key = 'addGroups'
            graphQLString = f'''mutation {{
                {key}(input: {{names: ["{'", "'.join(group_names)}"] }}) {{
                    groups {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if not isinstance(result, dict):
                return pd.DataFrame()

            groups = result[key]['groups']
            df = pd.DataFrame(groups)

            return df


    def users(
        self,
        fields: Optional[list] = None, 
        where: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame of available users
        """

        key = 'users'

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields =f'''
                id
                name
                username
                providerName
                providerUserId
                revision
            ''' 

        resolvedFilter = self._resolve_where(where)
        graphQLString = f'''query Users {{
            {key}{resolvedFilter}  {{
                {_fields}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif not isinstance(result, dict):
            raise Exception("Result is not a dictionary")
        df = pd.json_normalize(result[key])
        return df


    def userGroups(self, filter: Optional[str] = None) -> pd.DataFrame:
        """
        Returns a DataFrame of available user groups. User Groups can be filtered by name

        Parameters:
        -----------
        filter : str, optional
            Filters the user groups by name.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user group information. Returns id and name. 
        """
        key = 'groups'

        _fields = '''
            id
            name
        '''
        where_string = "" 
        if filter is not None:
            where_string = f'(where:{{name:{{eq:"{filter}"}}}})'

        graphQLString = f'''query userGroups {{
            {key}{where_string} {{
                {_fields}
            }}
        }}'''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)

        if result is None:
            return pd.DataFrame()
        elif not isinstance(result, dict):
            raise Exception("Result is not a dictionary")
        
        df = pd.json_normalize(result[key])

        return df
    

    def updatePermissions(self, group: str, permissions: list, permissionType: str) -> pd.DataFrame:
        
        """
        Updates permissions of a group and returns a pandas DataFrame with permission information.

        Parameters:
        -----------
        group : str
            The name of the group to update the permissions of.
        permissions : list
            A list of permissions to update. Permission are ["ADD","DELETE","READ","UPDATE"]
        permissionType : str
            The type of permission to update. PermissionTypes are "USERS", "USERS_GROUPS", "RULES", "ROLES", "DYNAMIC_OBJECT_TYPES", "SERVICE_ACCOUNTS", "EXTERNAL_RIGHTS" and "PERMISSIONS".

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with permission information. Returns groupId, type and id.
        """
        correlation_id = str(uuid4())

       
        _fields = '''
            groupId
            type
            id
        '''

        permission_df = self.getPermissionsOfGroups(filter = group) 
        if permission_df.empty:
            raise Exception(f"No permissions found for group {group}")
        permissionId = permission_df.loc[permission_df["permissions.type"] == permissionType, "permissions.id"].iloc[0]
        groupId = permission_df.loc[0, "id"]

        with logger.contextualize(correlation_id=correlation_id):
            key = 'updatePermissions'

            graphQLString = f'''mutation {{
                {key}(input: {{permissions: {{groupId:"{groupId}", id:"{permissionId}", permissions: {permissions}, type: {permissionType}}}, }}) {{
                    permissions {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result[key]['permissions'], meta =  ['groupId', 'type', 'id'])
            return df


    def addPermissions(self, group: str, permissions: list, permissionType: str) -> pd.DataFrame:
        """
        Adds one or more permissions to a group and returns a pandas DataFrame with permission information.

        Parameters:
        -----------
        group : str
            The name of the group to add the permissions to.
        permissions : list
            A list of permissions to add to the group. Permission are ["ADD","DELETE","READ","UPDATE"]
        permissionType : str
            The type of permission to add to the group. PermissionTypes are "USERS", "USERS_GROUPS", "RULES", "ROLES", "DYNAMIC_OBJECT_TYPES", "SERVICE_ACCOUNTS", "EXTERNAL_RIGHTS" and "PERMISSIONS".

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with permission information. Returns groupId, type and id.
        """
        correlation_id = str(uuid4())

    
        _fields = '''
            groupId
            type
            id
        '''

        groupId = self.userGroups(filter = group )["id"].iloc[0]

        with logger.contextualize(correlation_id=correlation_id):
            
            key = 'addPermissions'
            graphQLString = f'''mutation {{
                {key}(input: {{permissions: {{groupId:"{groupId}", permissions: {permissions}, type: {permissionType}}}}}) {{
                    permissions {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result[key]['permissions'], meta =  ['groupId', 'type', 'id'])

        return df


    def getPermissionsOfGroups(self, filter: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves all groups and their permissions, permissions can be filtered by group.

        Parameters:
        -----------
        filter : list, optional
            A list of group names to filter the results by.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame about permissions and which user group they belong to. 
            Returns name and id of the group, as well as id, permissions, type and revision of the perimissions of each group
        """

       
        _fields =f'''
            name
            id
            permissions{{
                id
                permissions
                type
                revision
            }}
        ''' 

        correlation_id = str(uuid4())
        where_string = "" 
        if filter is not None:
            where_string = f'(where:{{name:{{eq:"{filter}"}}}})'
       
        with logger.contextualize(correlation_id=correlation_id):
            key = 'permissionsOfGroups'
            graphQLString = f'''query {key} 
            {{groups {where_string}
                {{
                    {_fields}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result["groups"], 'permissions', ["name", "id"], record_prefix="permissions.")
            return df
    
    def serviceAccounts(
        self,
        fields:Optional[list] = None, 
        where:Optional[str] = None
        ) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame of available service accounts.
        """

        key = 'serviceAccounts'

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields =f'''
                id
                name
            ''' 

        resolvedFilter = self._resolve_where(where)
        graphQLString = f'''query ServiceAccounts {{
            {key}{resolvedFilter}  {{
                {_fields}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif not isinstance(result, dict):
            raise Exception("Result is not a dictionary")
        
        df = pd.json_normalize(result[key])
        return df

    def createRole(
        self,
        inventoryName:str, 
        roleName:str,
        userGroups:Optional[list] = None, 
        objectPermissions:list=['Create', 'Delete'], 
        propertiesPermissions:list=['Read', 'Update']
        ) -> None:

        """
        Creates a role and sets all rights to all properties

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory for which the new role authorizes rights.
        roleName : str
            Name of the new role.
        userGroup : list = None
            List of user group names. If None, the role will be created without attaching user groups.
        objectPermissions : list = ['Create', 'Delete']
            Default is 'Create' and 'Delete' to allow creating and deleting items of the specified inventory.
            Other entries are not allowed.
        propertiesPermissions : list = ['Read', 'Update']
            Default is 'Read' and 'Update'. All properties will receive 
            the specified rights. Other entries are not allowed.
            Permissions are not extended on referenced inventories!
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # Parameter validation
            try:
                self.techStack.metaData.structure[inventoryName]
            except:
                ErrorHandler.error(self.techStack.config.raiseException, f"Unknown inventory '{inventoryName}'")
                return
            
            try:
                roles = self.roles()
                if roleName in list(roles['name']):
                    ErrorHandler.error(self.techStack.config.raiseException, f"Role '{roleName}' already exists.")
                    return
            except:
                pass

            if isinstance(userGroups, str):
                userGroups = [userGroups]

            dfUserGroups = None
            if userGroups != None:
                # 'in' is not supported therefore load all groups
                dfUserGroups = self.userGroups()
                falseUserGroups = []
                for group in userGroups:
                    if group not in list(dfUserGroups['name']):
                        falseUserGroups.append(group)
                
                if falseUserGroups:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Unknown user group(s) {falseUserGroups}")
                    return

            # Create role
            properties = self.techStack.metaData.structure[inventoryName]['properties']

            ppstring = '[' + ','.join(map(str.upper, propertiesPermissions)) + ']'
            props = '[\n'
            refProps = '[\n'
            for _, value in properties.items():
                if value["type"] == 'scalar':
                    props += f'{{ propertyId: {GraphQLUtil.to_graphql(value["propertyId"])}\n permissions: {ppstring} }}\n'
                elif value["type"] == 'reference':
                    refProps += f'{{ propertyId: {GraphQLUtil.to_graphql(value["propertyId"])}\n inventoryId: {GraphQLUtil.to_graphql(value["inventoryId"])}\n propertyPermissions: {ppstring}\n inventoryPermissions: [NONE]\n properties: []\n referencedProperties: []\n }}'
            props += ']'
            refProps += ']'
            
            graphQLString= f'''
            mutation AddRole($roleName: String!, $inventoryId: String!, $inventoryPermissions: [ObjectPermission!]!) {{ 
                addRoles (input: {{
                    roles: {{
                        name: $roleName
                        rootInventoryPermission: {{
                            inventoryId: $inventoryId
                            inventoryPermissions: $inventoryPermissions
                            properties: {props}
                            referencedProperties: {refProps}
                            }}
                        }}
                    }})
                    {{
                    roles {{
                        id
                    }}
                }}
            }}
            '''
            params = {
                "roleName": roleName,
                "inventoryId": self.techStack.metaData.structure[inventoryName]['inventoryId'],
                "inventoryPermissions": list(map(str.upper, objectPermissions)),
            }

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId, params=params)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary")

            # if result['addRole']['errors']:
            #     GraphQLUtil.list_graphQl_errors(result, 'createInventory')
            #     return

            logger.info(f"Role {roleName} created.")

            roleId = result['addRoles']['roles'][0]['id']

            # Create rules
            if userGroups != None:
                for groupname in userGroups:
                    if (dfUserGroups is None or dfUserGroups.empty):
                        raise Exception("No user groups found")
                    
                    groupId = dfUserGroups.set_index('name').to_dict(orient='index')[groupname]['id']
                    createRuleGqlString= f'''
                    mutation AddRule($roleId: String!, $groupId: String!) {{
                        addRules (input: {{
                            rules: {{
                                roleId: $roleId
                                groupId: $groupId
                                filter: ""
                                filterFormat: EXPRESSION
                                }}
                            }})
                            {{
                            rules {{
                                ruleId
                            }}
                        }}
                    }}
                    '''
                    result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, createRuleGqlString, correlationId, params={"roleId": roleId, "groupId": groupId})
                    if result != None:
                        logger.info(f"Rule for {roleName} and user group {groupname} created.")
                    else:
                        logger.error(f"Rule for {roleName} and user group {groupname} could not be created.")

            return

    def deleteRole(self, role:str) -> None:
        """
        Deletes a role and all related rules.
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # Get Ids of roles and rules
            rolesResult = self.roles()
            roles = rolesResult.set_index('name')
            
            roleId = roles.loc[role, 'id']
            rules = self.rules()
            if (rules is None or rules.empty):
                raise Exception("No rules found")
            
            rules = rules.set_index('role.name')
            try:
                ruleId = rules.loc[role, 'id']
            except:
                ruleId = None
            ruleIds = [ruleId]

            # First delete rules
            if ruleIds:
                deleteRuleGraphQLString = f'''
                mutation deleteRule($ruleId: String!) {{
                    removeRule(input: {{
                        ruleId: $ruleId
                    }}) {{
                        ruleId
                    }}
                }}
                '''
                for ruleId in ruleIds:
                    result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, deleteRuleGraphQLString, correlationId, {"ruleId": ruleId})
                    if result != None:
                        logger.info(f"Rule {ruleId} of role {role} with id {ruleId} has been deleted.")
                    else:
                        ErrorHandler.error(self.techStack.config.raiseException, f"Rule {ruleId} of role {roleId} could not be deleted.")
                        return

            # After all rules have been deleted, delete the role
            deleteRoleGraphQLString = f'''
            mutation deleteRole($roleId: String!) {{
                removeRole(input: {{
                    roleId: $roleId
                }}) {{
                    roleId
                }}
            }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, deleteRoleGraphQLString, correlationId, {"roleId": roleId})
            if result != None:
                logger.info(f"Role {role} with id {roleId} has been deleted.")
            else:
                ErrorHandler.error(self.techStack.config.raiseException, f"Role {roleId} could not be deleted.")
            
            return
        

    def addRule(self, role: str, group: str, filter: str) -> str:
        """
        Adds a rule connecting role with usergroup and adds a filter to this rule.

        Parameters:
        -----------
        role : str
            The name of the role associated with the rule.
        group : str
            The name of the group to add the rule to.
        filter : str
            The filter to apply to the rule. The format must be:"Object.porpertyID=filter_value" 

        Returns:
        --------
        str
            The ID of the created rule.
        """
        roleId = self.roles(nameFilter =f'{role}')['id'].iloc[0]
        groupId = self.userGroups(filter =f'{group}')['id'].iloc[0]

        graphqlString = '''
            mutation AddRule($roleId: String!, $groupId: String!, $filter: String!) {
                addRules(input: {
                    rules: {
                        roleId: $roleId
                        groupId: $groupId
                        filter: $filter
                        filterFormat: EXPRESSION
                    }
                }) {
                    rules {
                        ruleId
                    }
                }
            }
        '''

        params = {
            "roleId": roleId,
            "groupId": groupId,
            "filter": filter
        }

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphqlString, params=params)

        if isinstance(result, dict):
            rule_id = result['addRules']['rules'][0]['ruleId']
            logger.info(f"Rule for {role} and user group {groupId} created with ID {rule_id}.")
            return rule_id
        else:
            ErrorHandler.error(self.techStack.config.raiseException, f"Rule could not be created.")
            return ''
