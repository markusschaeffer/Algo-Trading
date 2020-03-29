import pandas as pd
import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr


class Watchlist:

    # default Expressions for dynamodb table scan
    DEFAULTFILTEREXPRESSION = '#trading = :true OR #trading = :false'
    DEFAULTEXPRESSIONATTRIBUTEVALUES = {':true': True, ':false': False}
    DEFAULTEXPRESSIONATTRIBUTENAMES = {
        '#name': 'name', '#trading': 'trading'}
    DEFAULTPROJECTIONEXPRESSION = 'isin, #name, symbol, trading'

    def __init__(self, dynamoDBTableName='Watchlist'):
        '''
        @dynamoDBTableName: name of the dynamodb table, e.g. Watchlist
        '''

        self.dynamoDBTableName = dynamoDBTableName

        # specify dynamodb and table
        self.dynamodb = boto3.resource('dynamodb')
        self.client = boto3.client('dynamodb')
        self.table = self.dynamodb.Table(self.dynamoDBTableName)

    def addStock(self, stock):
        '''
        stores a single stock
        @stock: a dict containing isin, name, symbol, and trading as keys
        '''

        isin = stock['isin']
        name = stock['name']
        symbol = stock['symbol']
        trading = stock['trading']

        print('Adding stock:', isin, name, symbol, trading)

        # put item to dynamodb table
        self.table.put_item(
            Item={
                'isin': isin,
                'name': name,
                'symbol': symbol,
                'trading': trading
            }
        )

    def getStocks(self, filterExpression=DEFAULTFILTEREXPRESSION,
                  projectionExpression=DEFAULTPROJECTIONEXPRESSION,
                  expressionAttributeNames=DEFAULTEXPRESSIONATTRIBUTENAMES,
                  expressionAttributeValues=DEFAULTEXPRESSIONATTRIBUTEVALUES
                  ):
        '''
        @filterExpression:  
            specifies a condition that returns only items that satisfy the condition. All other items are discarded.
            e.g. Key('year').between(1950, 1959)
            or "#order_status = :delivered OR #order_status = :void OR #order_status = :bad",
        @projectionExpression:
            specifies the attributes you want in the scan result.
        @expressionAttributeNames:
            provides name substitution.
            e.g. {'#name': 'name'}
            or {"#order_status": "status"}
        @expressionAttributeValues:
            provides value substitution. You use this because you can't use literals in any expression, including KeyConditionExpression
            e.g. {":delivered": "delivered", ":void": "void", ":bad": "bad"}
        '''

        responseList = []

        # The scan method returns a subset of the items each time, called a page.
        response = self.table.scan(
            FilterExpression=filterExpression,
            ProjectionExpression=projectionExpression,
            ExpressionAttributeNames=expressionAttributeNames,
            ExpressionAttributeValues=expressionAttributeValues
        )

        if int(response['ResponseMetadata']['HTTPStatusCode']) == 200:
            responseList = response['Items']

        # When the last page is returned, LastEvaluatedKey is not part of the response.
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression=filterExpression,
                ProjectionExpression=projectionExpression,
                ExpressionAttributeNames=expressionAttributeNames,
                ExpressionAttributeValues=expressionAttributeValues,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            if int(response['ResponseMetadata']['HTTPStatusCode']) == 200:
                responseList = responseList+response['Items']

        return responseList

    def getFieldForStocks(self, field, filterExpression=DEFAULTFILTEREXPRESSION,
                          projectionExpression=DEFAULTPROJECTIONEXPRESSION,
                          expressionAttributeNames=DEFAULTEXPRESSIONATTRIBUTENAMES,
                          expressionAttributeValues=DEFAULTEXPRESSIONATTRIBUTEVALUES):
        '''
        returns all values for a specified field in the watchlist
        '''
        returnList = []
        stocksList = self.getStocks(filterExpression=filterExpression,
                                    projectionExpression=projectionExpression,
                                    expressionAttributeNames=expressionAttributeNames,
                                    expressionAttributeValues=expressionAttributeValues)
        for stock in stocksList:
            returnList.append(stock[field])
        return returnList

    def getSymbols(self, filterExpression=DEFAULTFILTEREXPRESSION,
                   projectionExpression=DEFAULTPROJECTIONEXPRESSION,
                   expressionAttributeNames=DEFAULTEXPRESSIONATTRIBUTENAMES,
                   expressionAttributeValues=DEFAULTEXPRESSIONATTRIBUTEVALUES):
        '''
        returns all stock symbols in the watchlist as a list of strings
        '''
        return self.getFieldForStocks('symbol', filterExpression=filterExpression,
                                      projectionExpression=projectionExpression,
                                      expressionAttributeNames=expressionAttributeNames,
                                      expressionAttributeValues=expressionAttributeValues)

    def getIsins(self, filterExpression=DEFAULTFILTEREXPRESSION, expressionAttributeValues=DEFAULTEXPRESSIONATTRIBUTEVALUES):
        '''
        returns all isins in the watchlist as a list of strings
        '''
        return self.getFieldForStocks('isin', filterExpression=filterExpression, expressionAttributeValues=expressionAttributeValues)

    def getIsinForSymbol(self, symbol):
        '''
        returns the isin for a single specified symbol
        '''

        fe = '#symbol = :sym'
        eav = {':sym': symbol}
        ean = {'#symbol': 'symbol'}
        pe = 'isin, symbol'

        isin = ''
        try:
            isin = self.getStocks(
                filterExpression=fe, projectionExpression=pe, expressionAttributeNames=ean, expressionAttributeValues=eav)[0]['isin']
        except ClientError as e:
            print(e.response['Error']['Message'])

        return isin

    def getNameForSymbol(self, symbol):
        '''
        returns the name for a single specified symbol
        @symbol: e.g. AMZN
        @name: e.g. Amazon
        '''
        name = ''
        try:
            isin = self.getIsinForSymbol(symbol)
            name = self.table.query(KeyConditionExpression=Key('isin').eq(isin))[
                'Items'][0]['name']
        except ClientError as e:
            print(e.response['Error']['Message'])

        return name
