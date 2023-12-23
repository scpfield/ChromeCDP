import  sys, os, time, signal, random, json, re, websocket, ssl, cdp, quopri, copy
import  multiprocessing as mp
import  multiprocessing.managers as mpm
from    colorama import Fore, Back, Style, init as colorama_init
from    websocket import ABNF

from    util import *
from    ChromeLauncher import ChromeLauncher
from    CDPDataWrappers import CDPEvent, CDPReturnValue
from    ScreenPrinter import Screen




class JavaScriptObject():

    GlobalThisObjectID = None
    WindowObjectID     = None

    def __init__(   self,
                    CDPClient       = None,
                    Name            = None,
                    Type            = None,
                    SubType         = None,
                    ClassName       = None,
                    Description     = None,
                    ObjectID        = None,
                    Value           = None):

        self.CDPClient              = CDPClient
        self.Name                   = Name
        self.Type                   = Type
        self.SubType                = SubType
        self.ClassName              = ClassName
        self.Description            = Description
        self.ObjectID               = ObjectID
        self.Value                  = Value
        self.PropertyObjects        = {}
        self.ArrayObjects           = []

        if self.Name == "null":
            self.Name = None        
        if self.Type == "null":
            self.Type = None
        if self.SubType == "null":
            self.SubType = None
        if self.ClassName == "null":
            self.ClassName = None
        if self.Description == "null":
            self.Description = None            
        if self.ObjectID == "null":
            self.ObjectID = None
        if self.Value == "null":
            self.Value = None


    @classmethod
    def GetGlobalThisObjectID( cls, CDPClient ):

        cls.GlobalThisObjectID   = None
        Script                   = 'globalThis;'
        ReturnValue              = CDPClient.ExecuteScript(
                                    expression      = Script,
                                    return_by_value = False)
        if not ReturnValue:
            print('Failed to get GlobalThisObjectID')
            Pause()
            return None

        cls.GlobalThisObjectID = (
            ReturnValue.Result.get('result').get('objectId'))

        if not cls.GlobalThisObjectID:
            print('Failed to get GlobalThisObjectID')
            Pause()
            return None

        print("GlobalThisObjectID = " + cls.GlobalThisObjectID)
        return cls.GlobalThisObjectID


    @classmethod
    def GetWindowObjectID( cls, CDPClient ):

        cls.WindowObjectID  = None
        Script              = 'window;'
        ReturnValue         = CDPClient.ExecuteScript(
                              expression      = Script,
                              return_by_value = False )

        if not ReturnValue:
            print('Failed to get GetWindowObjectID')
            Pause()
            return None

        cls.WindowObjectID = (
            ReturnValue.Result.get('result').get('objectId'))

        if not cls.WindowObjectID:
            print('Failed to get WindowObjectID')
            Pause()
            return None

        print("WindowObjectID = " + cls.WindowObjectID )
        return cls.WindowObjectID


    @classmethod
    def CreateFromObjectID( cls, ObjectID, CDPClient ):

        FunctionImpl = "globalThis.GetObjectInfo"

        Argument1    = cdp.runtime.CallArgument(
                        object_id = cdp.runtime.RemoteObjectId(
                        ObjectID ))

        TargetObject = cdp.runtime.RemoteObjectId(
                        JavaScriptObject.GlobalThisObjectID )

        ReturnValue  = CDPClient.ExecuteFunctionOn(
                        function_declaration = FunctionImpl,
                        object_id = TargetObject,
                        arguments = [ Argument1 ],
                        return_by_value = False )

        if ( not ReturnValue ) or ReturnValue.Error:
            print('Failed to get object info')
            Pause()
            return None

        NewObject = cls.CreateFromReturnValue( ReturnValue, CDPClient )

        return NewObject


    @classmethod
    def CreateFromReturnValue( cls, CDPReturnValue, CDPClient ):

        Result = None

        if not     ( Result := CDPReturnValue.Result.get( 'result'  )):
            if not ( Result := CDPReturnValue.Result.get( 'objects' )):
                print('Unable to find result/objects in CDP return value')
                Pause()
                return None

        NewObject   =   cls(
                        CDPClient    = CDPClient,
                        Name         = Result.get('name'),
                        Type         = Result.get('type'),
                        SubType      = Result.get('subtype'),
                        ClassName    = Result.get('className'),
                        Description  = Result.get('description'),
                        ObjectID     = Result.get('objectId'),
                        Value        = Result.get('value') )

        # set Name if missing
        if NewObject.Name == None:

            if NewObject.Value != None:
                NewObject.Name = NewObject.Value

            elif NewObject.ClassName:
                NewObject.Name = NewObject.ClassName

            elif NewObject.Description:
                NewObject.Name = NewObject.Description

            elif NewObject.Type:
                NewObject.Name = NewObject.Type


        NewObject.PropertyObjects = NewObject.GetPropertyObjects()
        NewObject.ArrayObjects    = NewObject.GetArrayObjects()

        return NewObject


    @classmethod
    def CreateFromPropertyItem( cls, PropertyItem, CDPClient ):

        #if not PropertyItem.get('value'):
        #    print(PropertyItem)
        #    Pause()
        #    return None
        
        if not PropertyItem.get('value'):
            PropertyItem['value'] = {}
        
        Name      = None
        NewObject = cls(
                    CDPClient = CDPClient,
                    Name         = PropertyItem.get('name'),
                    Type         = PropertyItem.get('value').get('type'),
                    SubType      = PropertyItem.get('value').get('subtype'),
                    ClassName    = PropertyItem.get('value').get('className'),
                    Description  = PropertyItem.get('value').get('description'),
                    ObjectID     = PropertyItem.get('value').get('objectId'),
                    Value        = PropertyItem.get('value').get('value') )
            
        return NewObject

    def GetArrayObjectLength( self ):
    
        if not self.IsArrayObject():
            return None
            
        ArrayLengthStr  = None
        ArrayLengthInt  = None
        SplitChar1      = '('
        SplitChar2      = ')'
        
        if (( self.Name == '[[Scopes]]' ) or
            ( 'Scopes' in self.Description )):
              
                SplitChar1 = '['
                SplitChar2 = ']'
            
        try:
        
            ArrayLengthStr = (
                self.Description
                .split( SplitChar1 )[-1]
                .split( SplitChar2 )[0]  )
            
            ArrayLengthInt = int( ArrayLengthStr )
                
        except BaseException:
            self.Print()
            print('Failed to parse ArrayLength')
            print('ArrayLengthStr = ', ArrayLengthStr )
            print('ArrayLengthInt = ', ArrayLengthInt)
            print('SplitChars = ', SplitChar1, SplitChar2 )
            Pause()
            return None
                
        return ArrayLengthInt
    
    def IsSameAs( self, OtherJavaScriptObject ):
    
        if ( self.ObjectID == None ):
            #self.Print()
            #print( 'self.ObjectID is None')
            #Pause()
            return False
        
        if ( OtherJavaScriptObject.ObjectID == None ):
            #OtherJavaScriptObject.Print()
            #print( 'OtherJavaScriptObject.ObjectID is None' )
            #Pause()
            return False
           
        FunctionImpl = "globalThis.IsSameObject"
        Argument1    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       self.ObjectID ))
        Argument2    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       OtherJavaScriptObject.ObjectID )) 
        TargetObject = cdp.runtime.RemoteObjectId( 
                       JavaScriptObject.GlobalThisObjectID )
        ReturnValue  = self.CDPClient.ExecuteFunctionOn(
                       function_declaration = FunctionImpl,
                       object_id            = TargetObject,
                       arguments            = [ Argument1, Argument2 ],
                       return_by_value      = False )

        ReturnObject = JavaScriptObject.CreateFromReturnValue(
                       ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to get ReturnObject')
            Pause()
            return False
        
        if ReturnObject.Value == None:
            print('Failed to get ReturnObject.Value')
            return False
        
        return( ReturnObject.Value )        
        
    
    def IsArrayObject( self ):
    
        if not self.ObjectID:
            return False
            
        if ( self.ClassName ) and ( self.ClassName == 'Array' ):
            return True
        
        if ( self.SubType ) and ( self.SubType == 'array' ):
            return True

        #if ( self.SubType ) and ( self.SubType == 'arraybuffer' ):
        #    return True

        if ( self.SubType ) and ( self.SubType == 'typedarray' ):
            return True


        return False

        
    def GetArrayObjects( self ):
        
        if not self.IsArrayObject():
            return None

        if self.Name == '[[Entries]]':
            self.Print()
            Pause()

        ArrayLength = self.GetArrayObjectLength()

        if ArrayLength == None:
            self.Print()
            Pause('Unable to get ArrayLength')
            return None
        
        if ArrayLength == 0:
            #self.Print()
            #print('Is Array with ArrayLength = 0')
            return []
            
        PropertyObjects = None

        if self.PropertyObjects:
            PropertyObjects = self.PropertyObjects
        else:
            PropertyObjects = self.GetPropertyObjects()

        if not PropertyObjects:
            self.Print()
            Pause('Unable to get PropertyObjects')
            return None
            
        ArrayObjects = []
            
        for Idx in range( ArrayLength ):
        
            ArrayObject = PropertyObjects.get( str(Idx) )

            if not ArrayObject:
                print('ArrayObject not found for Idx: ', Idx)
                Pause()
                continue

            # Set the Name of the Array item object
            if ArrayObject.Value != None:
                ArrayObject.Name = ArrayObject.Value

            elif ArrayObject.ClassName:
                ArrayObject.Name = ArrayObject.ClassName

            elif ArrayObject.Description:
                ArrayObject.Name = ArrayObject.Description

            elif ArrayObject.Type:
                ArrayObject.Name = ArrayObject.Type

            ArrayObjects.append( ArrayObject )

        return ArrayObjects


    def GetPropertyObjects( self ):

        if not self.ObjectID:
            return None

        if self.Type and ( self.Type == 'symbol' ):
            return None
            
        ReturnValue = self.CDPClient.ExecuteMethod(
            cdp.runtime.get_properties,
            object_id                   = cdp.runtime.RemoteObjectId( self.ObjectID ),
            own_properties              = False,
            accessor_properties_only    = False,
            generate_preview            = False,
            non_indexed_properties_only = False )

        if ( (ReturnValue == None) or (ReturnValue.Error != None) ):
            self.Print()
            print('Failed to get properties for object')
            Pause()
            return None
        
        PropertyObjects = {}

        for Category in ReturnValue.Result:
            
            for PropertyItem in ReturnValue.Result[Category]:
                
                if Category == 'internalProperties':
                
                    InternalList = [ '[[Prototype]]', '[[Scopes]]', '[[FunctionLocation]]',
                                      '[[PrimitiveValue]]', '[[IteratorHasMore]]', '[[IteratorIndex]]',
                                      '[[IteratorKind]]', '[[ArrayBufferByteLength]]', '[[ArrayBufferData]]',
                                      '[[Entries]]', '[[PromiseState]]' ]
                                      
                    PropertyName = PropertyItem.get('name')
                    if PropertyName not in InternalList:
                        self.Print()
                        print(PropertyName, Decorate=False, FileName="internalpropnames.txt")
                        print(PropertyItem)
                        # Pause()
                        
                    
                            
                if PropertyItem.get('value'):
                                
                    NewObject = JavaScriptObject.CreateFromPropertyItem(
                                PropertyItem, self.CDPClient)

                    PropertyObjects[NewObject.Name] = NewObject
                
                else:
                
                    SpecialTypes = ['get', 'set']
                    
                    for SpecialType in SpecialTypes:

                        NewPropertyItem         = copy.deepcopy( PropertyItem )
                        NewPropertyItem         = (
                            { 
                                'value'
                                if Key == SpecialType else Key : Value
                                for Key, Value in NewPropertyItem.items() 
                            } )
                        
                        if NewPropertyItem.get('value'):
                            NewPropertyItem['name'] = ( SpecialType + ' ' +
                                                        NewPropertyItem['name'] )
                                                    
                        #if 'epubCaptionSide' in NewPropertyItem['name']:
                        #    print( PropertyItem )
                        #    print( NewPropertyItem )
                        #    ReturnValue.Print()
                        #    Pause()
                            
                        NewObject = JavaScriptObject.CreateFromPropertyItem(
                                    NewPropertyItem, self.CDPClient )

                        PropertyObjects[NewObject.Name] = NewObject
        
        
        # Handle name adjustments
        NamePropertyObject  = PropertyObjects.get('name')
        SymbolTagObject     = PropertyObjects.get(
                              'Symbol(Symbol.toStringTag)')
                              
        if NamePropertyObject:
            self.Name    = NamePropertyObject.Value
            if self.Name == '':
                self.Name = '[Anonymous]'
        elif SymbolTagObject:
            self.Name = SymbolTagObject.Value
        else:    
            self.Name = self.ClassName
            
        # Handle [[FunctionLocation]]
        FunctionLocationPropertyObject = PropertyObjects.get('[[FunctionLocation]]')
        if FunctionLocationPropertyObject and FunctionLocationPropertyObject.Value != None:
            self.ScriptID   = FunctionLocationPropertyObject.Value.get('scriptId')
            self.LineNum    = FunctionLocationPropertyObject.Value.get('lineNumber')
            self.ColumnNum  = FunctionLocationPropertyObject.Value.get('columnNumber')
            
        # Handle [[Scopes]]
        ScopesPropertyObject = PropertyObjects.get('[[Scopes]]')
        if ScopesPropertyObject:
            ScopesArrayObjects = ScopesPropertyObject.GetArrayObjects()
            self.ScopesList = []
            if ScopesArrayObjects:
                for ScopesArrayObject in ScopesArrayObjects:
                    if ScopesArrayObject.Description:
                        self.ScopesList.append( ScopesArrayObject.Description )
        
        
        # Handle [[PrimitiveValue]]
        PrimitivePropertyObject = PropertyObjects.get('[[PrimitiveValue]]')
        if PrimitivePropertyObject and PrimitivePropertyObject.Value != None:
            self.SubType         = PrimitivePropertyObject.Type
            self.Description     = PrimitivePropertyObject.Value
            self.Value           = PrimitivePropertyObject.Value
            self.Print()
            print("Handle [[PrimitiveValue]]")
            #Pause()
            
        # Handle [[IteratorHasMore]]
        IteratorHasMorePropertyObject = PropertyObjects.get('[[IteratorHasMore]]')
        if IteratorHasMorePropertyObject and IteratorHasMorePropertyObject.Value != None:
            self.IteratorHasMore      = IteratorHasMorePropertyObject.Value
            self.Print()
            print("Handle [[IteratorHasMore]]")
            #Pause()            

        # Handle [[IteratorIndex]]
        IteratorIndexPropertyObject = PropertyObjects.get('[[IteratorIndex]]')
        if IteratorIndexPropertyObject and IteratorIndexPropertyObject.Value != None:
            self.IteratorIndex      = IteratorIndexPropertyObject.Value
            self.Print()
            print("Handle [[IteratorIndex]]")
            #Pause()

        # Handle [[IteratorKind]]
        IteratorKindPropertyObject = PropertyObjects.get('[[IteratorKind]]')
        if IteratorKindPropertyObject and IteratorKindPropertyObject.Value != None:
            self.IteratorKind      = IteratorKindPropertyObject.Value
            self.Print()
            print("Handle [[IteratorKind]]")
            #Pause()
            
        # Handle [[PromiseState]]
        PromiseStatePropertyObject = PropertyObjects.get('[[PromiseState]]')
        if PromiseStatePropertyObject and PromiseStatePropertyObject.Value != None:
            self.Value      = PromiseStatePropertyObject.Value
            self.Print()
            print("Handle [[PromiseState]]")
            #Pause()            

        # Handle [[ArrayBufferByteLength]]
        ArrayBufferByteLengthPropertyObject = PropertyObjects.get('[[ArrayBufferByteLength]]')
        if ArrayBufferByteLengthPropertyObject and ArrayBufferByteLengthPropertyObject.Value != None:
            self.ArrayBufferByteLength = ArrayBufferByteLengthPropertyObject.Value
            self.Print()
            print("Handle [[ArrayBufferByteLength]]")
            #Pause()

        # Handle [[ArrayBufferData]]
        ArrayBufferDataPropertyObject = PropertyObjects.get('[[ArrayBufferData]]')
        if ArrayBufferDataPropertyObject and ArrayBufferDataPropertyObject.Value != None:
            self.ArrayBufferData = ArrayBufferDataPropertyObject.Value
            self.Print()
            print("Handle [[ArrayBufferData]]")
            #Pause()

        # Handle [[Entries]]
        #EntriesPropertyObject = PropertyObjects.get('[[Entries]]')
        #if EntriesPropertyObject:
            #EntriesPropertyObject.ArrayObjects = EntriesPropertyObject.GetArrayObjects()
            #EntriesPropertyObject.Print()
            #self.Print()
            #print("Handle [[Entries]]")
            #Pause()
        
        if not self.Value:
            if (( self.Name         == "Object" ) and
                ( self.Type         == "object" ) and
                ( self.ClassName    == "Object" ) and
                ( self.Description  == "Object" )):
                    ReturnObject = self.CallGetObjectInfo()
                    if ReturnObject and ( ReturnObject.Value != '{}' ):
                        self.Value = ReturnObject.Value
                    
        return PropertyObjects

    def CallGetObjectInfo( self ):

        if not self.ObjectID:
            return None
            
        FunctionImpl    = "globalThis.GetObjectInfo"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          self.ObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
        
        if not ReturnValue or not ReturnValue.Result:
            return None
        
        ReturnObject = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to get ReturnObject')
            Pause()
            return None
            
        return( ReturnObject )

    def Print( self, Verbose = True, **kwargs ):
    
        OutputStr = ''
            
        if Verbose:
        
            OutputStr = json.dumps( self, 
                                    indent = 2,
                                    default = JavaScriptObjectSerializer )
                                    
            print( OutputStr, Decorate = False, **kwargs )
            
        else:

            if not self.PropertyObjects:
                self.PropertyObjects = self.GetPropertyObjects()
            
            if not self.ArrayObjects:
                self.ArrayObjects = self.GetArrayObjects()

            if self.Name:
                OutputStr += f"Name: {self.Name}, "

            if self.PropertyObjects:
                UniqueIDPropertyObject = self.PropertyObjects.get( '__UniqueID__' )
                if UniqueIDPropertyObject != None:
                    OutputStr += f"UniqueID: {UniqueIDPropertyObject.Value}, "
                
            if self.Type:        
                OutputStr += f"Type: {self.Type}, "

            if self.SubType:        
                OutputStr += f"SubType: {self.SubType}, "
            
            if self.ClassName:
                OutputStr += f"Class: {self.ClassName}, "

            if self.Type and self.Type == 'function':
                LengthPropertyObject = self.PropertyObjects.get( 'length' )
                if LengthPropertyObject and LengthPropertyObject.Value:
                    OutputStr += f"ArgCnt: {LengthPropertyObject.Value}, "
                else:
                    OutputStr += f"ArgCnt: 0, "
            
            if self.IsArrayObject():
                OutputStr += f"ArrayCnt: {self.GetArrayObjectLength()}, "            
            
            if self.PropertyObjects:
                PropertyCount = len( self.PropertyObjects )
                OutputStr += f"PropCnt: {PropertyCount}, "

            if self.Value != None:
                OutputStr += f"Value: {TruncateStr( self.Value, 25 )}, "
            
            if self.PropertyObjects and self.PropertyObjects.get('[[FunctionLocation]]'):
                OutputStr += (  f"ScriptId: {self.ScriptID}, " +
                                f"Line: {self.LineNum}, " +
                                f"Column: {self.ColumnNum}, " )

            if self.PropertyObjects and self.PropertyObjects.get('[[Scopes]]'):
                if self.ScopesList:
                    ScopesStr = ','.join(self.ScopesList)
                    OutputStr += f"Scopes: {ScopesStr}, "

            if (self.ClassName != None) and ( 'Text' in self.ClassName ):
                WholeTextPropertyObject = self.PropertyObjects.get('wholeText')
                if WholeTextPropertyObject and WholeTextPropertyObject.Value:
                    TruncatedText = TruncateStr( WholeTextPropertyObject.Value, 35 )
                    OutputStr += f"Text: '{TruncatedText}', "
           
            if self.Description != None:
                OutputStr += f"Desc: {self.Description}"
            
            OutputStr = OutputStr.strip().replace('\r', '').replace('\n', '').strip()
            
            print( OutputStr, Decorate = False, Truncate = 200, **kwargs )



class ChromeClient():

    def __init__( self ):

        try:
            self.ChromeProcess          = None
            self.ReaderProcess          = None
            self.EventProcess           = None
            self.WS                     = None
            self.SessionID              = None
            self.BrowserTargetInfo      = None
            self.PageTargetInfo         = None
            self.ReaderReadyEvent       = mp.Event()
            self.PageReadyEvent         = mp.Event()
            self.SendMutex              = mp.Lock()
            self.MessageID              = mp.Value("i", 0, lock = True)
            self.ChromeLauncher         = ChromeLauncher()
            self.CommandQueue           = mp.Queue()
            self.EventQueue             = mp.Queue()
            # self.EventProcessorStopFlag = mp.Value("b", False, lock = True)

            #( self.ReaderCommandPipe,
            #  self.ClientCommandPipe, ) = mp.Pipe()

            #( self.ReaderEventPipe,
            #  self.ClientEventPipe,   ) = mp.Pipe()

            # Hack to switch websocket._abnf lock class
            # to use the serializable multiprocess class
            websocket._abnf.Lock        = mp.Lock()

            # Launch Chrome
            self.ChromeProcess = self.ChromeLauncher.Launch()
            if not self.ChromeProcess:
                raise ChromeClientException("Failed to launch Chrome")

            # Get the Browser + Page target info from Chrome's special
            # HTTP URLs which provide the websocket URLs for each
            self.BrowserTargetInfo  = self.ChromeLauncher.GetBrowserTargetInfo()
            self.PageTargetInfo     = self.ChromeLauncher.GetPageTargetInfo()

            if (( not self.BrowserTargetInfo )  or
                ( not self.PageTargetInfo    )):
                raise ChromeClientException("Failed to get target info")

            # Create Page Session with Chrome
            if not self.CreateSession():
                raise ChromeClientException("Failed to create Chrome sessions")

        except BaseException as Failure:
            raise   ChromeClientException(
                    OriginalException = Failure )


    def CreateSession( self ):

        print("Creating Chrome Sessions")

        try:
            # Connect to the Page websocket URL
            if not self.Connect(
                URL = self.PageTargetInfo.get('webSocketDebuggerUrl')):
                return False

            # Start MessageReader process
            self.ReaderProcess = self.StartMessageReader()
            if not self.ReaderProcess:
                return False

            # Execute the CDP command to attach to the Page target
            # and it returns a Page sessionId
            ReturnValue     =   self.ExecuteMethod(
                                cdp.target.attach_to_target,
                                target_id = cdp.target.TargetID(
                                    self.PageTargetInfo['id'] ),
                                flatten = True )

            ReturnValue.Print()
            self.SessionID  = ReturnValue.CDPObject

            if not self.SessionID:
                print("Failed to get SessionID")
                return False

            # Execute CDP command to auto-attach to new Pages
            ReturnValue     =   self.ExecuteMethod(
                                cdp.target.set_auto_attach,
                                auto_attach = True,
                                flatten     = True,
                                wait_for_debugger_on_start = False )

            return True

        except BaseException as Failure:
            raise ChromeClientException(
                  OriginalException = Failure )

        ... # End of CreateSession


    def Connect( self, URL ):

        SSLOptions = {  'cert_reqs'      : ssl.CERT_NONE,
                        'check_hostname' : False }

        # Creating WebSocket class with multithread=False,
        # because all it does is synchronize calls to
        # socket.send() using the non-serializable threading.Lock
        # We will synchronize ourselves using mp.Lock

        try:
            self.WS = websocket.WebSocket(
                        sslopt              = SSLOptions,
                        enable_multithread  = False)

            # Try to connect with short timeout
            # then increase if connected

            self.WS.connect( URL,
                suppress_origin = True,
                timeout = 5 )

            if not self.WS.connected:
                return False

            print( f"Connected To: {URL}" )
            self.WS.settimeout( 20 )

            return True

        except BaseException as Failure:
            raise ChromeClientException(
                  OriginalException = Failure )


    def ExecuteMethod( self, CDPMethod, **kwargs ):

        #print("ExecuteMethod called")
        # The methods from the CDP package accept Python
        # objects that represent the Chrome data models,
        # and return generators which serializes them to
        # JSON dictionary format for transmission.
        #
        # The way it works is you call the generator twice.
        # First to serialize the full Chrome command.
        # Then a second time to process the response
        # from Chrome by de-serializing back into a Python object.
        #

        # First call the CDP method to get the generator,
        # initializing it with all the args for the call
        Generator       = CDPMethod( **kwargs )

        # Next, invoke the generator the first time
        # which returns a JSON dictionary of the Chrome
        # method with the args
        # note:  send(None) is the same as next()
        ChromeMethod    = Generator.send( None )

        # Now we send the command to Chrome and wait for response
        # The response is a JSON string, that we load as a JSON
        # dictionary.  Or we get a ChromeClientException.

        #print("Sending command: ", ChromeMethod)
        Response        = self.SendCommand( ChromeMethod )

        #print("Sent command: ", ChromeMethod)
        # Create a ReturnValue container for the Response
        # which stores the Chrome response in various forms
        ReturnValue     = CDPReturnValue( ChromeMethod, Response )

        if ReturnValue == None:
            print('Critical failure creating CDPReturnValue')
            Pause()
            return None

        if ReturnValue.Error != None:
            print('Received Error/Exception from CDP Protocol')
            ReturnValue.PrintError()
            Pause()
            return ReturnValue

        if ReturnValue.Result == None:
            print('Critical failure, CDPReturnValue.Result is None')
            Pause()
            return ReturnValue

        #
        # To convert the JSON dictionary response to a
        # python CDP object, you call the CDP generator
        # a second time.
        #
        # It converts and then delivers the python object
        # by raising a StopIteration which it adds the python
        # object of the result as an attribute of the Exception
        # itself. It's kind of weird but that's the way it works.
        #

        if ReturnValue.Result != {}:

            try:

                Generator.send( ReturnValue.Result )

                # Note: Some of the CDP return values
                # turn into Tuples after conversion to
                # Python objects.
                # Sometimes 2, 3 or 4 values depending
                # on the API call.

            except StopIteration as GeneratorResult:
                ReturnValue.CDPObject = GeneratorResult.value

            if ReturnValue.CDPObject == None:
                print('Failed to convert Result into CDPObject')
                ReturnValue.PrintResponse()
                Pause()
                return None

        return ReturnValue

        ... # End of Execute


    def __getstate__( self ):
        StateCopy = copy.copy( self.__dict__ )
        if 'ChromeLauncher' in StateCopy:
            del StateCopy['ChromeLauncher']
        if 'ChromeProcess' in StateCopy:
            del StateCopy['ChromeProcess']
        if 'ReaderProcess' in StateCopy:
            del StateCopy['ReaderProcess']
        if 'EventProcess' in StateCopy:
            del StateCopy['EventProcess']

        for k, v in StateCopy.items():
            print(k, ' = ', v)

        return StateCopy

    def ExecuteFunctionOn(  self,
                            function_declaration = None,
                            object_id = None,
                            arguments = None,
                            execution_context_id = None,
                            return_by_value = False ):

        if ( execution_context_id ):
        
            ReturnValue = self.ExecuteMethod(
                cdp.runtime.call_function_on,
                function_declaration = function_declaration,
                execution_context_id = cdp.runtime.ExecutionContextId(1),
                arguments = arguments,
                silent = False,
                return_by_value = return_by_value,
                generate_preview = False,
                user_gesture = True,
                await_promise = False,
                throw_on_side_effect = False,
                object_group = "mygroup" )
                
        elif ( object_id ):

            ReturnValue = self.ExecuteMethod(
                cdp.runtime.call_function_on,
                function_declaration = function_declaration,
                object_id = object_id,
                #arguments = arguments,
                silent = False,
                return_by_value = return_by_value,
                generate_preview = False,
                user_gesture = True,
                await_promise = False,
                throw_on_side_effect = False,
                object_group = "mygroup" )        

        return ReturnValue

    def ExecuteScript(  self, expression = None, return_by_value = False, context_id = 1 ):

        ReturnValue = self.ExecuteMethod(
            cdp.runtime.evaluate,
            expression                        = expression,
            object_group                      = "mygroup",
            return_by_value                   = return_by_value,
            #context_id                        = cdp.runtime.ExecutionContextId(context_id),
            generate_web_driver_value         = False,
            include_command_line_api          = True,
            silent                            = False,
            generate_preview                  = False,
            user_gesture                      = True,
            await_promise                     = True,
            throw_on_side_effect              = False,
            timeout                           = cdp.runtime.TimeDelta(60000),
            disable_breaks                    = True,
            repl_mode                         = True,
            allow_unsafe_eval_blocked_by_csp  = True)

        return ReturnValue


    # Start of execution for the EventProcessor process
    @staticmethod
    def EventProcessor( EventQueue,
                        PageReadyEvent,
                        ExecuteMethod,
                        ExecuteScript,
                        SendCommand,
                        PrintToScreen ):

        print('EventProcessor: Started')

        EventMessage                = None
        OutputScreen                = Screen()
        OutputScreen.ExecuteMethod  = ExecuteMethod
        OutputScreen.SendCommand    = SendCommand

        if PrintToScreen:
            OutputScreen.ScreenThread.start()

        try:

            while True:

                if PrintToScreen:
                    if not OutputScreen.ScreenThread.is_alive(): return False

                EventMessage  =  CDPEvent( EventQueue.get() )
                EventMessage.OutputScreen = OutputScreen

                if not EventMessage.CDPObject:
                    print('ERROR: Missing CDPObject!')
                    EventMessage.PrintMessage()
                    OutputScreen.CloseScreen()
                    os._exit(0)

                match type( EventMessage.CDPObject ):

                    #case cdp.debugger.ScriptParsed:
                    #    continue

                    case cdp.css.MediaQueryResultChanged:
                        if EventMessage.Params:
                            EventMessage.PrintToScreen()

                    case cdp.audits.IssueAdded:
                        EventMessage.PrintToScreen()
                        EventMessage.PrintMessage()

                    case cdp.page.FrameStoppedLoading:

                        EventMessage.PrintToScreen()
                        Result = ExecuteMethod( cdp.dom.get_document,
                                                depth = -1, pierce = True )
                        Result = ExecuteMethod( cdp.dom.request_child_nodes,
                                                node_id = cdp.dom.NodeId( 0 ),
                                                depth = -1, pierce = True   )

                    case cdp.page.LoadEventFired:

                        EventMessage.PrintToScreen()
                        Result = ExecuteMethod( cdp.dom.get_document,
                                                depth = -1, pierce = True )
                        Result = ExecuteMethod( cdp.dom.request_child_nodes,
                                                node_id = cdp.dom.NodeId( 0 ),
                                                depth = -1, pierce = True   )

                    case cdp.page.DomContentEventFired:

                        EventMessage.PrintToScreen()
                        Result = ExecuteMethod( cdp.dom.get_document,
                                                depth = -1, pierce = True )
                        Result = ExecuteMethod( cdp.dom.request_child_nodes,
                                                node_id = cdp.dom.NodeId( 0 ),
                                                depth = -1, pierce = True   )

                    case cdp.accessibility.LoadComplete:
                        EventMessage.PrintToScreen()
                        Result = ExecuteMethod( cdp.dom.get_document,
                                                depth = -1, pierce = True )
                        Result = ExecuteMethod( cdp.dom.request_child_nodes,
                                                node_id = cdp.dom.NodeId( 0 ),
                                                depth = -1, pierce = True   )

                        PageReadyEvent.set()
                        #PageReadyEvent.clear()

                    case cdp.accessibility.NodesUpdated:
                        EventMessage.PrintToScreen()
                        Result = ExecuteMethod( cdp.dom.get_document,
                                                depth = -1, pierce = True )
                        Result = ExecuteMethod( cdp.dom.request_child_nodes,
                                                node_id = cdp.dom.NodeId( 0 ),
                                                depth = -1, pierce = True   )

                    case cdp.dom.ChildNodeInserted:
                        EventMessage.PrintToScreen()
                        Result = ExecuteMethod( cdp.dom.get_document,
                                                depth = -1, pierce = True )
                        Result = ExecuteMethod( cdp.dom.request_child_nodes,
                                                node_id = cdp.dom.NodeId( 0 ),
                                                depth = -1, pierce = True   )

                    case cdp.css.FontsUpdated:

                        if EventMessage.Params:
                            EventMessage.PrintToScreen()

                    case cdp.console.MessageAdded:
                        continue

                    case cdp.fetch.RequestPaused:

                        EventMessage.PrintToScreen()
                        RequestID = EventMessage.CDPObject.request_id

                        Result = ExecuteMethod( cdp.fetch.continue_request,
                                                request_id = RequestID )


                    case cdp.runtime.ConsoleAPICalled:

                        EventMessage.PrintMessage()

                        DOMEvent =  EventMessage.Message
                        Excluded =  [ 'mousemove', 'pointermove', 'pointerrawupdate', '' ]

                        if not EventMessage.Params: continue

                        if EventMessage.DOMEventType not in Excluded:

                            EventMessage.GetDOMEventDetails(
                                         ExecuteMethod,
                                         SendCommand )

                            EventMessage.PrintToScreen()

                    case _:
                        EventMessage.PrintToScreen()

        except BaseException as Failure:
            print( GetExceptionInfo( Failure ))
        finally:
            print('EventProcessor exiting')
            print('Last Event:')
            EventMessage.PrintMessage()
            OutputScreen.CloseScreen()
            os._exit(0)


    # Start of execution for the MessageReader process
    @staticmethod
    def MessageReader(  WS,
                        CommandQueue,
                        EventQueue,
                        ReaderReadyEvent ):

        try:
            # Signal the ReadyEvent so clients will know
            ReaderReadyEvent.set()

            # Loop forever or until we are terminated
            while True:

                Opcode = Frame = Message = None

                # Block until a websocket message arrives
                ( Opcode,
                  Frame, )  = WS.recv_data( control_frame = False )

                # Process new message
                match Opcode:

                    case ABNF.OPCODE_TEXT:

                        # Load the text message as a JSON dictionary
                        Message = json.loads( Frame.decode('utf-8') )

                        # If there is an 'id' value, it means it is
                        # the result of a CDP function call command.
                        # If not, it is an async CDP event.

                        if Message.get('id') != None:

                            # Send the result to the caller
                            #ReaderCommandPipe.send( Message )
                            CommandQueue.put( Message )

                        else:
                            # Send the event to the event processor
                            #ReaderEventPipe.send( Message )
                            EventQueue.put( Message )

                    # Various other opcodes, not sure what to
                    # do with some of them
                    case ABNF.OPCODE_CONT:
                        print()
                        print( 'Control Frame Received:' )
                        print( Frame )
                        print()
                    case ABNF.OPCODE_BINARY:
                        print()
                        print( 'Binary Frame Received')
                        print()
                    case ABNF.OPCODE_CLOSE:
                        print()
                        print( 'Close Frame Received' )
                        print()
                        raise ChromeClientException("Close Frame Received")
                    case ABNF.OPCODE_PING:
                        print()
                        print( 'Ping Frame Received' )
                        print( Frame )
                        print()
                    case ABNF.OPCODE_PONG:
                        print()
                        print( 'Pong Frame Received' )
                        print( Frame )
                        print()
                    case _:
                        print()
                        print( 'Unknown Opcode Received' )
                        print( Frame )
                        print()
                        raise ChromeClientException("Unknown Frame Received")

        except BaseException as Failure:
            ReaderReadyEvent.clear()
            raise SystemExit


    def SendCommand( self, Command ):

        try:

            # The mp.Lock mutex is nice because it supports
            # the context manager which automatically
            # releases the lock even if an exception occurs

            # This is blocking call
            #with self.SendMutex:

            # If we got a string, load it as a JSON dict
            # to add the ID and Session values
            if isinstance( Command, str):
                Command = json.loads( Command )

            # Each command needs to have a unique ID
            # so we use an incrementing integer value
            Command['id'] = self.MessageID.value

            # The sessionId is optional, but we're using it
            if self.SessionID:
                Command['sessionId'] = self.SessionID

            # Now we need to serialize it to a JSON string
            # to send it to Chrome via websocket
            Command = json.dumps( Command )

            self.WS.send( Command, opcode = ABNF.OPCODE_TEXT )

            # The response arrives asychronously, and is
            # read by the MessagerReader process, which then
            # sends it here via the CommandPipe

            # This is blocking call
            #Response = self.ClientCommandPipe.recv()
            Response = self.CommandQueue.get()

            # Increment MessageID counter for the next call

            with self.MessageID.get_lock():
                self.MessageID.value += 1

            return Response

        except BaseException as Failure:
            return( ChromeClientException(
                    OriginalException = Failure ))


    def StartMessageReader( self ):

        try:

            # Create a MessageReader Process
            # A message-loop for incoming websocket messages

            self.ReaderReadyEvent.clear()

            ReaderProcess   =   mp.Process(
                                daemon  =   True,
                                target  =   self.MessageReader,
                                args    = ( self.WS,
                                            self.CommandQueue,
                                            self.EventQueue,
                                            self.ReaderReadyEvent, ))
            ReaderProcess.start()

            # After launching the process, wait for it to
            # give the Ready signal
            self.ReaderReadyEvent.wait()
            return ReaderProcess

        except BaseException as Failure:
            raise ChromeClientException(
                  OriginalException = Failure)


    def StopMessageReader( self ):

        if (( self.ReaderProcess) and
            ( self.ReaderProcess.is_alive())):

            try:

                print("Killing MessageReaderProcess")
                #self.ReaderProcess.kill()

            except BaseException as ExpectedFailure:
                PrintExceptionInfo( ExpectedFailure )


    def StartEventProcessor( self, PrintToScreen = True ):

        try:
            # Create the Event Processor process.
            # It just loops on receiving events from
            # Chrome via a pipe connection with the
            # MessageReader, and prints them
            #
            # It also can make outbound calls and
            # all it needs are the class methods
            # for sending messages.
            EventProcess =  mp.Process(
                            daemon  =   True,
                            target  =   self.EventProcessor,
                            args    = ( self.EventQueue,
                                        self.PageReadyEvent,
                                        self.ExecuteMethod,
                                        self.ExecuteScript,
                                        self.SendCommand,
                                        PrintToScreen ))

            EventProcess.start()

            if EventProcess:
                self.EventProcess = EventProcess
                return True
            else:
                self.EventProcess = None
                return False

        except BaseException as Failure:
            self.EventProcess = None
            raise  ChromeClientException(
                   OriginalException = Failure)

    def StopEventProcessor( self ):

        if (( self.EventProcess) and
            ( self.EventProcess.is_alive())):

            try:
                print("Killing EventProcess")
                self.EventProcess.kill()
            except BaseException as ExpectedFailure:
                print( GetExceptionInfo(ExpectedFailure))

    def CloseChrome( self ):
        return;
        if  (( self.ChromeProcess   )   and
             ( self.ReaderProcess   )   and
             ( self.WS.connected    )):
                ReturnValue = self.ExecuteMethod( cdp.browser.close )
                ReturnValue.Print()

        ... # End of CDPClient class


class ChromeClientException( BaseException ):
    def __init__(self, OriginalException = None, *args, **kwargs ):
        super().__init__(*args, **kwargs)
        self.OriginalException = OriginalException


def JavaScriptObjectSerializer( Instance ):

    if isinstance( Instance, JavaScriptObject ):

        CopyOfInstanceDict = copy.copy( Instance.__dict__ )
        del CopyOfInstanceDict['CDPClient']
        return CopyOfInstanceDict



def main():
    print("Hello World")


if __name__ == '__main__':
    mp.freeze_support()
    colorama_init( autoreset = False )
    main()

