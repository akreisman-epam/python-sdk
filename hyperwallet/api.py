#!/usr/bin/env python

import os

from config import SERVER
from exceptions import HyperwalletException
from utils import ApiClient

from hyperwallet import (
    User,
    BankAccount,
    PrepaidCard,
    PaperCheck,
    Webhook
)


class Api(object):
    '''
    A Python interface for the Hyperwallet API.

    :param username:
        The username of this API user. **REQUIRED**
    :param password:
        The password of this API user. **REQUIRED**
    :param programToken:
        The token for the program this user is accessing. **REQUIRED**
    :param server:
        Your UAT or Production API URL if applicable.

    .. note::
        **server** defaults to the Hyperwallet Sandbox URL if not provided.

    '''

    def __init__(self,
                 username=None,
                 password=None,
                 programToken=None,
                 server=SERVER):
        '''
        Create an instance of the API interface.
        This is the main interface the user will call to interact with the API.
        '''

        if not username:
            raise HyperwalletException('username is required')

        if not password:
            raise HyperwalletException('password is required')

        if not programToken:
            raise HyperwalletException('programToken is required')

        self.username = username
        self.password = password
        self.programToken = programToken
        self.server = server

        self.apiClient = ApiClient(self.username, self.password, self.server)

    def _addProgramToken(self, data):
        '''
        Add the program token to the data object.

        :param data:
            A dictionary containing values defining a resource. **REQUIRED**
        :returns:
            A dictionary containing the provided values and the program token.
        '''

        if not isinstance(data, dict):
            raise HyperwalletException('data must be a dictionary object')

        if 'programToken' in data:
            return data

        data['programToken'] = self.programToken

        return data

    def _getCollection(self,
                       func=None,
                       params=None):
        '''
        Get A Collection of a Resource Type.

        A wrapper for any List function.

        :param func:
            The List function to wrap.
        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Resources.
        '''

        offset = params.get('offset') or 0
        maximum = None or params.get('maximum')

        # Return an empty array if the maximum is a negative number.
        if maximum is not None and maximum < 1:
            return []

        results = []
        chunksize = 100

        while True:
            response = func({'offset': offset, 'limit': chunksize})
            results += response
            offset += chunksize

            # If the response is smaller than the chunk we could have expected,
            # we know this is the last of the data available
            if len(response) < chunksize:
                break

            # Break if the total results exceed the maximum we wanted to return
            if maximum and len(results) >= maximum:
                break

        return results[0:maximum]

    def getUsers(self,
                 params=None):
        '''
        Get Users.

        A wrapper for the listUsers function. Provides an easy mechanism to
        return a slice of all Users between a given **offset** and **maximum**.

        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Users.
        '''

        return self._getCollection(self.listUsers, params)

    def listUsers(self,
                  params=None):
        '''
        List Users.

        :param params:
            A dictionary containing query parameters.
        :returns:
            An array of Users.
        '''

        response = self.apiClient.doGet('users', params)

        return [User(x) for x in response.get('data', [])]

    def createUser(self,
                   data=None):
        '''
        Create a User.

        :param data:
            A dictionary containing User information. **REQUIRED**
        :returns:
            A User.
        '''

        if not data:
            raise HyperwalletException('data is required')

        self._addProgramToken(data)

        response = self.apiClient.doPost('users', data)

        return User(response)

    def retrieveUser(self,
                     userToken=None):
        '''
        Retrieve a User.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :returns:
            A User.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken)
        )

        return User(response)

    def updateUser(self,
                   userToken=None,
                   data=None):
        '''
        Update a User.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param data:
            A dictionary containing User information. **REQUIRED**
        :returns:
            A User.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not data:
            raise HyperwalletException('data is required')

        response = self.apiClient.doPut(
            os.path.join('users', userToken),
            data
        )

        return User(response)

    def listUserBalances(self,
                         userToken=None,
                         params=None):
        '''
        List User Balances.

        :param userToken: A token identifying the User. **REQUIRED**
        :param params: A dictionary containing query parameters.
        :returns: The List User Balances API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        return self.apiClient.doGet(
            os.path.join('users', userToken, 'balances'),
            params
        )

    def listUserReceipts(self,
                         userToken=None,
                         params=None):
        '''
        List User Receipts.

        :param userToken: A token identifying the User. **REQUIRED**
        :param params: A dictionary containing query parameters.
        :returns: The List User Receipts API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        return self.apiClient.doGet(
            os.path.join('users', userToken, 'receipts'),
            params
        )

    def getBankAccounts(self,
                        params=None):
        '''
        Get Bank Accounts.

        A wrapper for the listBankAccounts function. Provides an easy mechanism
        to return a slice of all Bank Accounts between a given **offset** and
        **maximum**.

        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Bank Accounts.
        '''

        return self._getCollection(self.listBankAccounts, params)

    def listBankAccounts(self,
                         userToken=None,
                         params=None):
        '''
        List Bank Accounts.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param params:
            A dictionary containing query parameters.
        :returns:
            An array of Bank Accounts.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken, 'bank-accounts'),
            params
        )

        return [BankAccount(x) for x in response.get('data', [])]

    def createBankAccount(self,
                          userToken=None,
                          data=None):
        '''
        Create a Bank Account.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param data:
            A dictionary containing Bank Account information. **REQUIRED**
        :returns:
            A Bank Account.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not data:
            raise HyperwalletException('data is required')

        response = self.apiClient.doPost(
            os.path.join('users', userToken, 'bank-accounts'),
            data
        )

        return BankAccount(response)

    def retrieveBankAccount(self,
                            userToken=None,
                            bankAccountToken=None):
        '''
        Retrieve a Bank Account.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param bankAccountToken:
            A token identifying the Bank Account. **REQUIRED**
        :returns:
            A Bank Account.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not bankAccountToken:
            raise HyperwalletException('bankAccountToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken, 'bank-accounts', bankAccountToken)
        )

        return BankAccount(response)

    def updateBankAccount(self,
                          userToken=None,
                          bankAccountToken=None,
                          data=None):
        '''
        Update a Bank Account.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param bankAccountToken:
            A token identifying the Bank Account. **REQUIRED**
        :param data:
            A dictionary containing Bank Account information. **REQUIRED**
        :returns:
            A Bank Account.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not bankAccountToken:
            raise HyperwalletException('bankAccountToken is required')

        if not data:
            raise HyperwalletException('data is required')

        response = self.apiClient.doPut(
            os.path.join(
                'users',
                userToken,
                'bank-accounts',
                bankAccountToken
            ),
            data
        )

        return BankAccount(response)

    def createBankAccountStatusTransition(self,
                                          userToken=None,
                                          bankAccountToken=None,
                                          data=None):
        '''
        Create a Bank Account Status Transition.

        :param userToken: A token identifying the User. **REQUIRED**
        :param bankAccountToken:
            A token identifying the Bank Account. **REQUIRED**
        :param data:
            A dictionary containing Bank Account Status Transition information.
            **REQUIRED**
        :returns: The Create a Bank Account Status Transition API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not bankAccountToken:
            raise HyperwalletException('bankAccountToken is required')

        if not data:
            raise HyperwalletException('data is required')

        return self.apiClient.doPost(
            os.path.join(
                'users',
                userToken,
                'bank-accounts',
                bankAccountToken,
                'status-transitions'
            ),
            data
        )

    def retrieveBankAccountStatusTransition(self,
                                            userToken=None,
                                            bankAccountToken=None,
                                            statusTransitionToken=None):
        '''
        Retrieve a Bank Account Status Transition.

        :param userToken: A token identifying the User. **REQUIRED**
        :param bankAccountToken:
            A token identifying the Bank Account. **REQUIRED**
        :param statusTransitionToken:
            A token identifying the Bank Account Status Transition.
            **REQUIRED**
        :returns: The Retrieve a Bank Account Status Transition API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not bankAccountToken:
            raise HyperwalletException('bankAccountToken is required')

        if not statusTransitionToken:
            raise HyperwalletException('statusTransitionToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'users',
                userToken,
                'bank-accounts',
                bankAccountToken,
                'status-transitions',
                statusTransitionToken
            )
        )

    def getPrepaidCards(self,
                        params=None):
        '''
        Get Prepaid Cards.

        A wrapper for the listPrepaidCards function. Provides an easy mechanism
        to return a slice of all Prepaid Cards between a given **offset** and
        **maximum**.

        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Prepaid Cards.
        '''

        return self._getCollection(self.listPrepaidCards, params)

    def listPrepaidCards(self,
                         userToken=None,
                         params=None):
        '''
        List Prepaid Cards.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param params:
            A dictionary containing query parameters.
        :returns:
            An array of Prepaid Cards.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken, 'prepaid-cards'),
            params
        )

        return [PrepaidCard(x) for x in response.get('data', [])]

    def createPrepaidCard(self,
                          userToken=None,
                          data=None):
        '''
        Create a Prepaid Card.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param data:
            A dictionary containing Prepaid Card information. **REQUIRED**
        :returns:
            A Prepaid Card.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not data:
            raise HyperwalletException('data is required')

        response = self.apiClient.doPost(
            os.path.join('users', userToken, 'prepaid-cards'),
            data
        )

        return PrepaidCard(response)

    def retrievePrepaidCard(self,
                            userToken=None,
                            prepaidCardToken=None):
        '''
        Retrieve a Prepaid Card.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param prepaidCardToken:
            A token identifying the Prepaid Card. **REQUIRED**
        :returns:
            A Prepaid Card.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not prepaidCardToken:
            raise HyperwalletException('prepaidCardToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken, 'prepaid-cards', prepaidCardToken)
        )

        return PrepaidCard(response)

    def listPrepaidCardStatusTransitions(self,
                                         userToken=None,
                                         prepaidCardToken=None):
        '''
        List Status Transitions for Prepaid Card.

        :param userToken: A token identifying the User. **REQUIRED**
        :param prepaidCardToken:
            A token identifying the Prepaid Card. **REQUIRED**
        :returns: The List Status Transitions for Prepaid Card API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not prepaidCardToken:
            raise HyperwalletException('prepaidCardToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'users',
                userToken,
                'prepaid-cards',
                prepaidCardToken,
                'status-transitions'
            )
        )

    def createPrepaidCardStatusTransition(self,
                                          userToken=None,
                                          prepaidCardToken=None,
                                          data=None):
        '''
        Create a Prepaid Card Status Transition.

        :param userToken: A token identifying the User. **REQUIRED**
        :param prepaidCardToken:
            A token identifying the Prepaid Card. **REQUIRED**
        :param data:
            A dictionary containing Prepaid Card Status Transition information.
            **REQUIRED**
        :returns: The Create a Prepaid Card Status Transition API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not prepaidCardToken:
            raise HyperwalletException('prepaidCardToken is required')

        if not data:
            raise HyperwalletException('data is required')

        return self.apiClient.doPost(
            os.path.join(
                'users',
                userToken,
                'prepaid-cards',
                prepaidCardToken,
                'status-transitions'
            ),
            data
        )

    def retrievePrepaidCardStatusTransition(self,
                                            userToken=None,
                                            prepaidCardToken=None,
                                            statusTransitionToken=None):
        '''
        Retrieve a Prepaid Card Status Transition.

        :param userToken: A token identifying the User. **REQUIRED**
        :param prepaidCardToken:
            A token identifying the Prepaid Card. **REQUIRED**
        :param statusTransitionToken:
            A token identifying the Prepaid Card Status Transition.
            **REQUIRED**
        :returns: The Retrieve a Prepaid Card Status Transition API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not prepaidCardToken:
            raise HyperwalletException('prepaidCardToken is required')

        if not statusTransitionToken:
            raise HyperwalletException('statusTransitionToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'users',
                userToken,
                'prepaid-cards',
                prepaidCardToken,
                'status-transitions',
                statusTransitionToken
            )
        )

    def listPrepaidCardBalances(self,
                                userToken=None,
                                prepaidCardToken=None,
                                params=None):
        '''
        List Prepaid Card Balances.

        :param userToken: A token identifying the User. **REQUIRED**
        :param prepaidCardToken:
            A token identifying the Prepaid Card. **REQUIRED**
        :param params: A dictionary containing query parameters.
        :returns: The List Prepaid Card Balances API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not prepaidCardToken:
            raise HyperwalletException('prepaidCardToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'users',
                userToken,
                'prepaid-cards',
                prepaidCardToken,
                'balances'
            ),
            params
        )

    def listPrepaidCardReceipts(self,
                                userToken=None,
                                prepaidCardToken=None,
                                params=None):
        '''
        List Prepaid Card Receipts.

        :param userToken: A token identifying the User. **REQUIRED**
        :param prepaidCardToken:
            A token identifying the Prepaid Card. **REQUIRED**
        :param params: A dictionary containing query parameters.
        :returns: The List Prepaid Card Receipts API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not prepaidCardToken:
            raise HyperwalletException('prepaidCardToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'users',
                userToken,
                'prepaid-cards',
                prepaidCardToken,
                'receipts'
            ),
            params
        )

    def getPaperChecks(self,
                       params=None):
        '''
        Get Paper Checks.

        A wrapper for the listPaperChecks function. Provides an easy mechanism
        to return a slice of all Paper Checks between a given **offset** and
        **maximum**.

        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Paper Checks.
        '''

        return self._getCollection(self.listPaperChecks, params)

    def listPaperChecks(self,
                        userToken=None,
                        params=None):
        '''
        List Paper Checks.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param params:
            A dictionary containing query parameters.
        :returns:
            An array of Paper Checks.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken, 'paper-checks'),
            params
        )

        return [PaperCheck(x) for x in response.get('data', [])]

    def createPaperCheck(self,
                         userToken=None,
                         data=None):
        '''
        Create a Paper Check.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param data:
            A dictionary containing Paper Check information. **REQUIRED**
        :returns:
            A Paper Check.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not data:
            raise HyperwalletException('data is required')

        response = self.apiClient.doPost(
            os.path.join('users', userToken, 'paper-checks'),
            data
        )

        return PaperCheck(response)

    def retrievePaperCheck(self,
                           userToken=None,
                           paperCheckToken=None):
        '''
        Retrieve a Paper Check.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param paperCheckToken:
            A token identifying the Paper Check. **REQUIRED**
        :returns:
            A Paper Check.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not paperCheckToken:
            raise HyperwalletException('paperCheckToken is required')

        response = self.apiClient.doGet(
            os.path.join('users', userToken, 'paper-checks', paperCheckToken)
        )

        return PaperCheck(response)

    def updatePaperCheck(self,
                         userToken=None,
                         paperCheckToken=None,
                         data=None):
        '''
        Update a Paper Check.

        :param userToken:
            A token identifying the User. **REQUIRED**
        :param paperCheckToken:
            A token identifying the Paper Check. **REQUIRED**
        :param data:
            A dictionary containing Paper Check information. **REQUIRED**
        :returns:
            A Paper Check.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not paperCheckToken:
            raise HyperwalletException('paperCheckToken is required')

        if not data:
            raise HyperwalletException('data is required')

        response = self.apiClient.doPut(
            os.path.join('users', userToken, 'paper-checks', paperCheckToken),
            data
        )

        return PaperCheck(response)

    def createPaperCheckStatusTransition(self,
                                         userToken=None,
                                         paperCheckToken=None,
                                         data=None):
        '''
        Create a Paper Check Status Transition.

        :param userToken: A token identifying the User. **REQUIRED**
        :param paperCheckToken:
            A token identifying the Paper Check. **REQUIRED**
        :param data:
            A dictionary containing Paper Check Status Transition information.
            **REQUIRED**
        :returns: The Create a Paper Check Status Transition API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not paperCheckToken:
            raise HyperwalletException('paperCheckToken is required')

        if not data:
            raise HyperwalletException('data is required')

        return self.apiClient.doPost(
            os.path.join(
                'users',
                userToken,
                'paper-checks',
                paperCheckToken,
                'status-transitions'
            ),
            data
        )

    def retrievePaperCheckStatusTransition(self,
                                           userToken=None,
                                           paperCheckToken=None,
                                           statusTransitionToken=None):
        '''
        Retrieve a Paper Check Status Transition.

        :param userToken: A token identifying the User. **REQUIRED**
        :param paperCheckToken:
            A token identifying the Paper Check. **REQUIRED**
        :param statusTransitionToken:
            A token identifying the Paper Check Status Transition. **REQUIRED**
        :returns: The Retrieve a Paper Check Status Transition API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not paperCheckToken:
            raise HyperwalletException('paperCheckToken is required')

        if not statusTransitionToken:
            raise HyperwalletException('statusTransitionToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'users',
                userToken,
                'paper-checks',
                paperCheckToken,
                'status-transitions',
                statusTransitionToken
            )
        )

    def getPayments(self,
                    params=None):
        '''
        Get Payments.

        A wrapper for the listPayments function. Provides an easy mechanism
        to return a slice of all Payments between a given **offset** and
        **maximum**.

        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Payments.
        '''

        return self._getCollection(self.listPayments, params)

    def listPayments(self,
                     params=None):
        '''
        List Payments.

        :param params:
            A dictionary containing query parameters.
        :returns:
            An array of Payments.
        '''

        response = self.apiClient.doGet('payments', params)

        return [Payment(x) for x in response.get('data', [])]

    def createPayment(self,
                      data=None):
        '''
        Create a Payment.

        :param data:
            A dictionary containing Payment information. **REQUIRED**
        :returns:
            A Payment.
        '''

        if not data:
            raise HyperwalletException('data is required')

        self._addProgramToken(data)

        response = self.apiClient.doPost('payments', data)

        return Payment(response)

    def retrievePayment(self,
                        paymentToken=None):
        '''
        Retrieve a Payment.

        :param paymentToken:
            A token identifying the Payment. **REQUIRED**
        :returns:
            A Payment.
        '''

        if not paymentToken:
            raise HyperwalletException('paymentToken is required')

        response = self.apiClient.doGet(os.path.join('payments', paymentToken))

        return Payment(response)

    def retrieveAccount(self,
                        programToken=None,
                        accountToken=None):
        '''
        Retrieve an Account.

        :param programToken: A token identifying the Program. **REQUIRED**
        :param accountToken: A token identifying the Account. **REQUIRED**
        :returns: The Retrieve an Account API response.
        '''

        if not programToken:
            raise HyperwalletException('programToken is required')

        if not accountToken:
            raise HyperwalletException('accountToken is required')

        return self.apiClient.doGet(
            os.path.join('programs', programToken, 'accounts', accountToken)
        )

    def listAccountBalances(self,
                            programToken=None,
                            accountToken=None,
                            params=None):
        '''
        List Account Balances.

        :param programToken: A token identifying the Program. **REQUIRED**
        :param accountToken: A token identifying the Account. **REQUIRED**
        :param params: A dictionary containing query parameters.
        :returns: The List Account Balances API response.
        '''

        if not programToken:
            raise HyperwalletException('programToken is required')

        if not accountToken:
            raise HyperwalletException('accountToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'programs',
                programToken,
                'accounts',
                accountToken,
                'balances'
            ),
            params
        )

    def listAccountReceipts(self,
                            programToken=None,
                            accountToken=None,
                            params=None):
        '''
        List Account Receipts.

        :param programToken: A token identifying the Program. **REQUIRED**
        :param accountToken: A token identifying the Account. **REQUIRED**
        :param params: A dictionary containing query parameters.
        :returns: The List Account Receipts API response.
        '''

        if not programToken:
            raise HyperwalletException('programToken is required')

        if not accountToken:
            raise HyperwalletException('accountToken is required')

        return self.apiClient.doGet(
            os.path.join(
                'programs',
                programToken,
                'accounts',
                accountToken,
                'receipts'
            ),
            params
        )

    def retrieveProgram(self,
                        programToken=None):
        '''
        Retrieve a Program.

        :param programToken: A token identifying the Program. **REQUIRED**
        :returns: The Retrieve a Program API response.
        '''

        if not programToken:
            raise HyperwalletException('programToken is required')

        return self.apiClient.doGet(os.path.join('programs', programToken))

    def listTransferMethodConfigurations(self,
                                         params={}):
        '''
        List Transfer Method Configurations.

        :param params: A dictionary containing query parameters. **REQUIRED**
        :returns: The List Transfer Method Configurations API response.

        .. warning::
            **userToken** must be present in the params dictionary.
        '''

        if 'userToken' not in params:
            raise HyperwalletException('userToken is required')

        return self.apiClient.doGet('transfer-method-configurations', params)

    def retrieveTransferMethodConfiguration(self,
                                            params={}):
        '''
        Retrieve a Transfer Method Configuration.

        :param params: A dictionary containing query parameters. **REQUIRED**
        :returns: The Retrieve a Transfer Method Configuration API response.

        .. warning::
            **userToken** must be present in the params dictionary.

        .. warning::
            **country** must be present in the params dictionary.

        .. warning::
            **currency** must be present in the params dictionary.

        .. warning::
            **type** must be present in the params dictionary.

        .. warning::
            **profileType** must be present in the params dictionary.
        '''

        if 'userToken' not in params:
            raise HyperwalletException('userToken is required')

        if 'country' not in params:
            raise HyperwalletException('country is required')

        if 'currency' not in params:
            raise HyperwalletException('currency is required')

        if 'type' not in params:
            raise HyperwalletException('type is required')

        if 'profileType' not in params:
            raise HyperwalletException('profileType is required')

        return self.apiClient.doGet('transfer-method-configurations', params)

    def createTransferMethod(self,
                             userToken=None,
                             cacheToken=None,
                             data=None):
        '''
        Create a Transfer Method.

        :param userToken: A token identifying the User. **REQUIRED**
        :param cacheToken:
            A cache token identifying the Transfer Method. **REQUIRED**
        :param data: A dictionary containing Field Restriction information.
        :returns: The Create a Transfer Method API response.
        '''

        if not userToken:
            raise HyperwalletException('userToken is required')

        if not cacheToken:
            raise HyperwalletException('cacheToken is required')

        headers = {'Json-Cache-Token': cacheToken}

        return self.apiClient.doPost(
            os.path.join('users', userToken, 'transfer-methods'),
            data,
            headers
        )

    def getWebhooks(self,
                    params=None):
        '''
        Get Webhooks.

        A wrapper for the listWebhooks function. Provides an easy mechanism
        to return a slice of all Webhooks between a given **offset** and
        **maximum**.

        :param params:
            A dictionary containing parameters to slice with.
        :returns:
            An array of Webhooks.
        '''

        return self._getCollection(self.listWebhooks, params)

    def listWebhooks(self,
                     params=None):
        '''
        List Webhook Notifications.

        :param params:
            A dictionary containing query parameters.
        :returns:
            An array of Webhooks.
        '''

        response = self.apiClient.doGet('webhook-notifications', params)

        return [Webhook(x) for x in response.get('data', [])]

    def retrieveWebhook(self,
                        webhookToken=None):
        '''
        Retrieve a Webhook Notification.

        :param webhookToken:
            A token identifying the Webhook. **REQUIRED**
        :returns:
            A Webhook.
        '''

        if not webhookToken:
            raise HyperwalletException('webhookToken is required')

        response = self.apiClient.doGet(
            os.path.join('webhook-notifications', webhookToken)
        )

        return Webhook(response)
