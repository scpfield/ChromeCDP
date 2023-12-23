import  sys, os, time, signal, random, json, websocket, ssl, socket, ctypes
import  multiprocessing as mp
import  multiprocessing.managers as mpm
import  multiprocessing.connection as mpc
import  cdp
from    websocket import ABNF
from    ChromeLauncher import ChromeLauncher
from    util import *
from    colorama import Fore, Back, Style, init as colorama_init
from    ChromeClient import *

class Foo:
    ...
    
class ChromeClientApp():

    def __init__( self, Config = None ):

        signal.signal( signal.SIGINT,   self.OSSignalHandler )
        signal.signal( signal.SIGBREAK, self.OSSignalHandler )
        signal.signal( signal.SIGABRT,  self.OSSignalHandler )

        self.CDPClient = ChromeClient()


    def AddJavaScriptInjection( self ):
        
        ScriptFile = '.\JavaScriptInjections.js'
        ScriptText = None
        
        with open(ScriptFile, 'r', newline='', encoding='utf-8') as InputFile:
            ScriptText = ''.join(InputFile.readlines())

        if not ScriptText:
            print('Failed to load: ', ScriptFile)
            os.exit(0)
        
        ReturnValue = self.CDPClient.ExecuteMethod( 
                        cdp.page.add_script_to_evaluate_on_new_document,
                        source = ScriptText, 
                        world_name = None, 
                        include_command_line_api = True)
                        
        ReturnValue.Print()

        
    def InitializeCDP( self ):
        
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.log.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.page.enable ) 
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.page.set_lifecycle_events_enabled, enabled = True )
        
        JavaScriptObject.GetGlobalThisObjectID( self.CDPClient )
        JavaScriptObject.GetWindowObjectID( self.CDPClient )
        self.AddJavaScriptInjection()
        
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.dom.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.dom_snapshot.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.dom_storage.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.debugger.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.runtime.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.css.enable )
        # ReturnValue = self.CDPClient.ExecuteMethod( cdp.network.enable )
        # ReturnValue = self.CDPClient.ExecuteMethod( cdp.fetch.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.accessibility.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.audits.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.inspector.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.overlay.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.profiler.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.performance.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.service_worker.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.layer_tree.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.media.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.console.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.database.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.animation.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.indexed_db.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.heap_profiler.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.security.enable )
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.web_authn.enable )

        ReturnValue = self.CDPClient.ExecuteMethod( cdp.dom.get_document,
                                                 depth = -1, pierce = True )
                              
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.dom.request_child_nodes,
                                                 node_id = cdp.dom.NodeId( 0) , 
                                                 depth = -1, pierce = True )
        
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.browser.get_version )
        ReturnValue.Print()

        ... # done initializing
        
    def Test( self ):
    
        #URL = 'https://localhost:8834/#/'
        URL = 'file:///C:/python/sam/html/main.html'
        ReturnValue = self.CDPClient.ExecuteMethod( cdp.page.navigate, url = URL )
        #ReturnValue.Print()
        
        JavaScriptObject.GetGlobalThisObjectID( self.CDPClient )
        JavaScriptObject.GetWindowObjectID( self.CDPClient )
        self.AddJavaScriptInjection()
      
        #print("Waiting for PageReadyEvent")
        #self.CDPClient.PageReadyEvent.wait()
        #self.CDPClient.PageReadyEvent.clear()
        #print("Got PageReadyEvent!")
        
        #ReturnValue = self.CDPClient.ExecuteMethod( cdp.dom.get_document,
        #                                        depth = -1, pierce = True )
                                            
        #ReturnValue.Print()
        
        TestObject = JavaScriptObject.CreateFromReturnValue( 
                     ReturnValue, self.CDPClient)        
        
        TestObject.Print( Verbose = True )
        TestObject.PropertyObjects = TestObject.GetPropertyObjects()
        TestObject.ArrayObjects = TestObject.GetArrayObjects()
        TestObject.Print( Verbose = True )
        
        print(TestObject.ObjectID)
        
        '''
        if ReturnList and ReturnList.IsArrayObject():
            if ReturnList.ArrayObjects:
                print("Length = ", ReturnList.GetArrayObjectLength())
                for ArrayObject in ReturnList.ArrayObjects:
                
                        ArrayObject.PropertyObjects = ArrayObject.GetPropertyObjects()
                        ArrayObject.ArrayObjects = ArrayObject.GetArrayObjects()
                        ArrayObject.Print( Verbose = False, FileName="final.txt" )
        '''                

    def CallAddToGlobalTestMap( self, MyObject ):

        FunctionImpl    = "globalThis.AddToGlobalTestMap"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          MyObject.ObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
            
        ReturnObject    = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to create ReturnObject')
            Pause()
            return None
            
        return( ReturnObject.Value )



    def CallCreateEvent( self, DocumentObjectID ):

        print("CALL CREATE EVENT")
        print(DocumentObjectID)
        
        FunctionImpl    = "function () { this.Permissions(); }"
        
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          DocumentObjectID )
        
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                            function_declaration = FunctionImpl,
                            object_id = TargetObject,
                            return_by_value = True )
        
        # ReturnValue.Print()
        
        ReturnObject    = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to create ReturnObject')
            Pause()
            return None
        
        #ReturnObject.Print()
        
        return( ReturnObject )
        
    def CallGlobalTestMapHas( self, MyObject ):

        FunctionImpl    = "globalThis.GlobalTestMapHas"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          MyObject.ObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
        
        ReturnObject    = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to create ReturnObject')
            Pause()
            return None
            
        return( ReturnObject.Value )

    
    def CallGetGlobalTestMap( self ):

        FunctionImpl    = "globalThis.GetGlobalTestMap"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          return_by_value = False )
        ReturnObject    = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to create ReturnObject')
            Pause()
            return None
            
        return( ReturnObject )    
        
    
    def RecurseAllObjects( self, MyJavaScriptObject, Level = None, Label=None ):
    
        if Level == None:
            Level = 0
            
        if Label == None:
            Label = ''
            
        Indent = ( '     ' * Level )
        
        if not MyJavaScriptObject.ObjectID:
            return
        
        if MyJavaScriptObject.IsArrayObject():
            if not MyJavaScriptObject.GetArrayObjectLength():
                return
        else:
        
            #ObjectProperties = MyJavaScriptObject.GetPropertyObjects()
            #if ObjectProperties:
                #UniqueID = ObjectProperties.get('__UniqueID__')
                #if UniqueID and ( UniqueID.Value != None ):
                    #print("SEEN BEFORE: " + str(UniqueID.Value), Decorate=False, FileName="seen.txt")
                    #MyJavaScriptObject.Print( Verbose = False, FileName="seen.txt")
                    
        
            if self.CallGlobalTestMapHas( MyJavaScriptObject ):
                return
                
            if not self.CallAddToGlobalTestMap( MyJavaScriptObject ):
                print("Failed to add MyJavaScriptObject to GlobalTestMap", Decorate=False)
                MyJavaScriptObject.Print( Verbose = False )
                #Pause()
                return
                

            print( Label, Decorate = False, end = '', FileName="seen.txt" )
            MyJavaScriptObject.PropertyObjects = MyJavaScriptObject.GetPropertyObjects()
            MyJavaScriptObject.Print( Verbose = False, FileName="seen.txt" )   
                
        if MyJavaScriptObject.IsArrayObject():
            
            if not MyJavaScriptObject.ArrayObjects:
                MyJavaScriptObject.ArrayObjects = MyJavaScriptObject.GetArrayObjects()
        
            if MyJavaScriptObject.ArrayObjects:
            
                for Idx, ArrayObject in enumerate( MyJavaScriptObject.ArrayObjects ):
                                        
                    if not ArrayObject.ObjectID:
                        continue
                        
                    if (( MyJavaScriptObject.Name == '[[Scope]]' ) or 
                        ( 'Scope' in MyJavaScriptObject.Description )):
                       continue
                    
                    self.RecurseAllObjects( ArrayObject, Level = (Level + 1), Label = f"A-{Idx}: " )
                    
                return

                        
        if not MyJavaScriptObject.PropertyObjects:
            MyJavaScriptObject.PropertyObjects = MyJavaScriptObject.GetPropertyObjects()
        
        if MyJavaScriptObject.PropertyObjects:
        
            for Idx, (PropertyName, PropertyObject) in enumerate(
                                                       list( MyJavaScriptObject.PropertyObjects.items() )):

                if not PropertyObject.ObjectID:
                    continue
                                                       
                self.RecurseAllObjects( PropertyObject, Level = (Level + 1), Label = f"P-{Idx}: " )
            
            return

        return


    def GetProtoTypeInstances( self, Evaluation = None, NextInstance = None ):
        
        ReturnValue         = None
        EvalObject          = None
        ProtoTypeList       = []
        
        
        print("************* START ****************" )
        
        if Evaluation != None:
        
            ReturnValue =   self.CDPClient.ExecuteScript( 
                            expression = Evaluation,
                            return_by_value = False )

            ReturnValue.Print()
            #if ( not ReturnValue ) or ( ReturnValue.Error ):
            #    print( 'Failed to execute Evaluation' )
            #    Pause()
            #    return None
            
            EvalObject = JavaScriptObject.CreateFromReturnValue( 
                         ReturnValue, self.CDPClient )
            
            if not EvalObject:
                print('Failed to create EvalObject')
                Pause()
                return None        

            #if (( 'prototype' in Evaluation )   or 
            #    ( '__proto__' in Evaluation )):
            #        ProtoTypeList.append( EvalObject )
        
        else:

            if ( NextInstance != None ):
                #print("Setting EvalObject to NextInstance")
                EvalObject = NextInstance
        
        
        if EvalObject.Type == 'symbol':
            print( 'ObjectType cannot be symbol' )
            Pause()
            return None
        
        
        Exclusions = [  'GlobalSeenData', 'CallProtoProperty', 'CallGetProtoTypeOf',
                        'GetGlobalSeenData', 'IsSeenProtoType', 'AddSeenProtoType',
                        'IsSeenInstance', 'AddSeenInstance', 'GlobalEventListener',
                        'AddListenerToAllEvents', 'EventTypesAdded', 'TestObject',
                        'TestClass', 'GetObjectInfo' ]
        
        for Exclusion in Exclusions:
            if (( EvalObject.Description ) and 
                ( Exclusion in EvalObject.Description )):
                    return

        if EvalObject.ObjectID:
            if not EvalObject.IsArrayObject():
                # ProtoTypeList.append( EvalObject )
                ProtoTypeOfObject = self.CallGetProtoTypeOf( EvalObject )
                if ProtoTypeOfObject:
                    ProtoTypeList.append( ProtoTypeOfObject )
        
        if EvalObject.ArrayObjects:
            for ArrayObject in EvalObject.ArrayObjects:
                if ArrayObject.ObjectID:
                    #ArrayObject.Print()
                    ProtoTypeOfObject = self.CallGetProtoTypeOf( ArrayObject )
                    if ProtoTypeOfObject:                    
                        ProtoTypeList.append( ProtoTypeOfObject )
    
        elif EvalObject.PropertyObjects:
            for PropertyName, PropertyObject in EvalObject.PropertyObjects.items():
                if PropertyObject.ObjectID:
                    ProtoTypeOfObject = self.CallGetProtoTypeOf( PropertyObject )
                    if ProtoTypeOfObject:
                        ProtoTypeList.append( ProtoTypeOfObject )
        
        print("Total ProtoTypes Before Calling QueryObjects: ", len(ProtoTypeList))
        
        RecurseList = []
        InstanceMap = {}
        
        for ProtoIdx, ProtoTypeObject in enumerate(ProtoTypeList):
        
            for Exclusion in Exclusions:
                if (( ProtoTypeObject.Description ) and 
                    ( Exclusion in ProtoTypeObject.Description )):
                        #print(  ProtoIdx, ": Skipping ProtoType because Exclusion: ", 
                        #        ProtoTypeObject.Name, ProtoTypeObject.ClassName, 
                        #        ProtoTypeObject.Type, ProtoTypeObject.ObjectID )                    
                        continue
                    
            if ProtoTypeObject.ObjectID == None:
                #print( ProtoIdx, ": Skipping ProtoType because No ObjectID: ", 
                #        ProtoTypeObject.Name, ProtoTypeObject.ClassName, 
                #        ProtoTypeObject.Type, ProtoTypeObject.ObjectID )                    
                continue
            
            if self.IsSeenProtoType( ProtoTypeObject.ObjectID ):
                #print( ProtoIdx, ": Skipping ProtoType because IsSeenProtoType: ", 
                #        ProtoTypeObject.Name, ProtoTypeObject.ClassName, 
                #        ProtoTypeObject.Type, ProtoTypeObject.ObjectID )
                continue
                
            if not self.AddToSeenProtoTypeMap( ProtoTypeObject.ObjectID ):
                print( ProtoIdx, ": Failed to AddToSeenProtoTypeMap")
                
            print( ProtoIdx, ": Calling QueryObjects for ProtoType: ", 
                    ProtoTypeObject.Name, ProtoTypeObject.ClassName, 
                    ProtoTypeObject.Type, ProtoTypeObject.ObjectID )
            
            ReturnValue =   self.CDPClient.ExecuteMethod(  
                                cdp.runtime.query_objects,
                                object_group = "mygroup",
                                prototype_object_id = 
                                cdp.runtime.RemoteObjectId(
                                ProtoTypeObject.ObjectID ))
            
            InstanceArrayObject = JavaScriptObject.CreateFromReturnValue( 
                                   ReturnValue, self.CDPClient )            
        
            if not InstanceArrayObject:
                ReturnValue.Print()
                print('Failed to create InstanceArrayObject')
                Pause()
                continue
        
            if not InstanceArrayObject.IsArrayObject():
                InstanceArrayObject.Print()
                print('InstanceArrayObject from QueryObjects is not an array')
                Pause()
                continue
                
            InstanceArrayLength = InstanceArrayObject.GetArrayObjectLength()
            
            if not InstanceArrayLength:
                print( ProtoIdx, ": No Instances Returned for ProtoType: ", 
                        ProtoTypeObject.Name, ProtoTypeObject.ClassName, 
                        ProtoTypeObject.Type, ProtoTypeObject.ObjectID )
                continue

            print(ProtoIdx, ": QueryObjects returned ", InstanceArrayLength, " instances")
            
            InstanceMap[ProtoTypeObject] = InstanceArrayObject.ArrayObjects
            
            
        for ProtoTypeOfInstance, InstanceObjectList in InstanceMap.items():
   
            InstanceObjectLength = len(InstanceObjectList)
            
            for Idx, InstanceObject in enumerate(InstanceObjectList):
            
                for Exclusion in Exclusions:
                    if (( InstanceObject.Description ) and 
                        ( Exclusion in InstanceObject.Description )):
                            print("Instance is Excluded, skipping")
                            continue
            
                print()
                print( "Checking Instance Idx #", Idx, " of ", InstanceObjectLength)
                print( "Proto: ", Decorate=False, end='')
                ProtoTypeOfInstance.Print( Verbose = False )
                print( "Inst: ", Decorate=False, end='')
                InstanceObject.Print( Verbose = False )
                        
                    
                if self.IsSeenInstance( ProtoTypeOfInstance.ObjectID,
                                        InstanceObject.ObjectID ):
                                        
                    print("ProtoType-Instance pair is seen already, skipping")
                    continue
            
                if not self.AddToSeenInstanceSet( 
                            ProtoTypeOfInstance.ObjectID,
                            InstanceObject.ObjectID ):
                
                    print('Failed to add to SeenInstanceSet: ')
                    continue

                RecurseList.append( InstanceObject )
                    
        
        RecurseListLength = len(RecurseList)
        # print("Length of RecurseList: " + str(RecurseListLength) )
        #Pause()
        
        for Idx, InstanceObject in enumerate(RecurseList):
        
            if InstanceObject.IsArrayObject():
                ArrayLength = InstanceObject.GetArrayObjectLength()
                if not ArrayLength:
                    #InstanceObject.Print()
                    #print("Length = ", ArrayLength)
                    #Pause('NOT Recursing into empty array')
                    continue
                else:
                    print('Recursing into array of length: ', ArrayLength)
            
            if (( InstanceObject.Name == '[[Scopes]]' ) or
                ( 'Scopes' in str(InstanceObject.Description) )):
                    print('NOT Recursing into [[Scopes]]')
                    #Pause()
                    continue
                
            if not InstanceObject.PropertyObjects:
                InstanceObject.PropertyObjects = InstanceObject.GetPropertyObjects()
            
            if not InstanceObject.ArrayObjects:
                InstanceObject.ArrayObjects = InstanceObject.GetArrayObjects()
            
            print(  "Recursing Instance Idx #", Idx, " of ", RecurseListLength, "(",
                    InstanceObject.Name, InstanceObject.Type, 
                    InstanceObject.ClassName, InstanceObject.Description, 
                    InstanceObject.ObjectID, ")")
            
            self.GetProtoTypeInstances( NextInstance = InstanceObject )
            print(  "Popped out of recursion" )
    
    
    def CallGetProtoTypeOf( self, MyObject ):

        FunctionImpl    = "globalThis.CallGetProtoTypeOf"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          MyObject.ObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
            
        ProtoTypeObject = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ProtoTypeObject:
            print('Failed to get ProtoTypeObject')
            Pause()
            return None
            
        return( ProtoTypeObject )

    def CallGetObjectInfo( self, MyObject ):

        FunctionImpl    = "globalThis.GetObjectInfo"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          MyObject.ObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
        
        if not ReturnValue or not ReturnValue.Result:
            return None
            
        ReturnValue.Print()
        
        ReturnObject = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to get ReturnObject')
            Pause()
            return None
            
        return( ReturnObject )


    def CallProtoProperty( self, ObjectID ):

        FunctionImpl    = "globalThis.CallProtoProperty"
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          ObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
        
        ProtoTypeObject = JavaScriptObject.CreateFromReturnValue(
                          ReturnValue, self.CDPClient )

        if not ProtoTypeObject:
            print('Failed to get ProtoTypeObject')
            Pause()
            return None
            
        return( ProtoTypeObject )
        
    
    def AddToSeenInstanceSet( self, ProtoTypeObjectID, InstanceObjectID ):
    
        FunctionImpl = "globalThis.AddSeenInstance"
        Argument1    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       ProtoTypeObjectID ))
        Argument2    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       InstanceObjectID )) 
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
            return None
        
        return( ReturnObject.Value )
        
                    
    def AddToSeenProtoTypeMap( self, ProtoTypeObjectID ):
        
        FunctionImpl    = "globalThis.AddSeenProtoType"                
        TargetObject    = cdp.runtime.RemoteObjectId( 
                          JavaScriptObject.GlobalThisObjectID )
        Argument1       = cdp.runtime.CallArgument(
                          object_id = cdp.runtime.RemoteObjectId( 
                          ProtoTypeObjectID ))
        ReturnValue     = self.CDPClient.ExecuteFunctionOn(
                          function_declaration = FunctionImpl,
                          object_id = TargetObject,
                          arguments = [ Argument1 ],
                          return_by_value = False )
    
            
        ReturnObject = JavaScriptObject.CreateFromReturnValue(
                       ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to get ReturnObject')
            Pause()
            return None
            
        return( ReturnObject.Value )
        
        
    def IsSeenProtoType( self, ProtoTypeObjectID ):
    
        FunctionImpl        =   "globalThis.IsSeenProtoType"
        Argument1           =   cdp.runtime.CallArgument(
                                object_id = cdp.runtime.RemoteObjectId( 
                                ProtoTypeObjectID ))
        TargetObject        =   cdp.runtime.RemoteObjectId( 
                                JavaScriptObject.GlobalThisObjectID )
        ReturnValue         =   self.CDPClient.ExecuteFunctionOn(
                                function_declaration = FunctionImpl,
                                object_id = TargetObject,
                                arguments = [ Argument1 ],
                                return_by_value = False )
        
        ReturnObject = JavaScriptObject.CreateFromReturnValue(
                       ReturnValue, self.CDPClient )

        if not ReturnObject:
            print('Failed to get ReturnObject')
            Pause()
            return None
            
        return( ReturnObject.Value )
        
    def IsSeenInstance( self, ProtoTypeObjectID, InstanceObjectID ):
    
        FunctionImpl = "globalThis.IsSeenInstance"
        Argument1    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       ProtoTypeObjectID ))
        Argument2    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       InstanceObjectID )) 
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
            return None
            
        return( ReturnObject.Value )
        
        
    def CallJSONStringify( self, ObjectID ):
    
        FunctionImpl = "globalThis.CallJSONStringify"
        Argument1    = cdp.runtime.CallArgument(
                       object_id = cdp.runtime.RemoteObjectId( 
                       ObjectID ))
        TargetObject = cdp.runtime.RemoteObjectId( 
                       JavaScriptObject.GlobalThisObjectID )
        ReturnValue  = self.CDPClient.ExecuteFunctionOn(
                       function_declaration = FunctionImpl,
                       object_id            = TargetObject,
                       arguments            = [ Argument1 ],
                       return_by_value      = True )

        #ReturnValue.Print()
        if not ReturnValue:
            return None
            
        ReturnObject = JavaScriptObject.CreateFromReturnValue(
                       ReturnValue, self.CDPClient )

        #ReturnObject.Print()
        
        if not ReturnObject:
            print('Failed to get ReturnObject')
            Pause()
            return None
            
        return( ReturnObject.Value )
        
        
    def DumpGlobalSeenData( self ):
    
        FunctionImpl = 'globalThis.GetGlobalSeenData'
        TargetObject = cdp.runtime.RemoteObjectId( 
                       JavaScriptObject.GlobalThisObjectID )
        ReturnValue  = self.CDPClient.ExecuteFunctionOn(
                       function_declaration = FunctionImpl,
                       object_id = TargetObject,
                       arguments = None,
                       return_by_value = False )
        
        DataObjects =   JavaScriptObject.CreateFromReturnValue( 
                         ReturnValue, self.CDPClient )
        
        print("DataObjects Length: ", len(DataObjects.ArrayObjects))
        
        for ProtoIdx, DataObject in enumerate( DataObjects.ArrayObjects ):
        
            DataObject.PropertyObjects = DataObject.GetPropertyObjects()
            DataObject.ArrayObjects    = DataObject.GetArrayObjects()
            
            ProtoTypeObject = DataObject.PropertyObjects.get('ProtoTypeObject')
            
            ProtoTypeObject.PropertyObjects = ProtoTypeObject.GetPropertyObjects()
            ProtoTypeObject.ArrayObjects    = ProtoTypeObject.GetArrayObjects()
            
            print( '\n', Decorate = False, FileName = "dump.txt" )
            
            ProtoTypeObject.Print( Verbose = False, FileName = "dump.txt" )
                
            InstanceObjects = DataObject.PropertyObjects.get('InstanceObjects')
            
            InstanceObjects.PropertyObjects = InstanceObjects.GetPropertyObjects()
            InstanceObjects.ArrayObjects    = InstanceObjects.GetArrayObjects()
            
            for InstanceIdx, InstanceObject in enumerate(InstanceObjects.ArrayObjects):
                
                InstanceObject.PropertyObjects  = InstanceObject.GetPropertyObjects()
                InstanceObject.ArrayObjects     = InstanceObject.GetArrayObjects()
                
                Indent = '     '
                print( Indent, Decorate = False, FileName = "dump.txt", end='')
                InstanceObject.Print( Verbose = False, FileName = "dump.txt" )  
                
                
        
    def OSSignalHandler( self, Signal, Frame ):
        try:
            print( f'Caught Signal: ' +
                   f'{signal.strsignal(Signal)}' )
                
            os._exit(1)
            
        except SystemExit:
            print('SystemExit')
        except InterruptedError:
            print('InterruptedError')        
        except BaseException as Failure:
            print( GetExceptionInfo(Failure) )
        finally:
            ... #self.CDPClient.CloseChrome()


def main():
        
    try:

        ClientApp = ChromeClientApp()
        
        #ClientApp.CDPClient.StartEventProcessor( PrintToScreen = False )
        
        ClientApp.InitializeCDP()
        
        ClientApp.Test()
        # ClientApp.DumpGlobalSeenData()
        
        #ClientApp.CDPClient.StopEventProcessor()
            
        #if ClientApp.CDPClient.ChromeProcess:
        #    ClientApp.CDPClient.CloseChrome()
            
        #ClientApp.CDPClient.StopMessageReader()            
            
    except BaseException as Failure:
        print( GetExceptionInfo( Failure ) )
    finally:
        ClientApp.CDPClient.CloseChrome()
                
    
    while True:
        print("Looping")
        time.sleep(1)
        
    
if __name__ == '__main__':
    mp.freeze_support()
    colorama_init( autoreset = False )
    main()
    
