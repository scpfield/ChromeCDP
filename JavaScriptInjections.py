import sys, os

AddPageLoadListeners = (

    "   addEventListener( 'load', (evt) =>                       " +
    "   {                                                               " +
    "       console.log( evt );                                         " +
    "   },  false )                                                   " +
    "                                                                   " +
    "   document.addEventListener( 'readystatechange', (evt) =>         " +
    "   {                                                               " +
    "       console.log( evt );                                         " +
    "   },  false )                                                    " +
    "                                                                   " +
    "   document.addEventListener( 'DOMContentLoaded', (evt) =>         " +
    "   {                                                               " +
    "       console.log( evt );                                         " +
    "   },  false )                                                    " +
    "                                                                   " +
    "   document.addEventListener( 'click', (evt) =>                    " +
    "   {                                                               " +
    "       console.log( evt );                                         " +
    "   },  false )                                                    " +
    "                                                                   " )

AddAllEventsListener = (
    "                                                                       " +
    "   addAllEventsListener( target, listener, ...Args )          " +
    "   {                                                                   " +
    "        for (const key in target)                                      " +
    "        {                                                              " +
    "            if (/^on/.test(key))                                       " +
    "            {                                                          " +
    "                const eventType = key.substr(2);                       " +
    "                target.addEventListener(                               " +
    "                    eventType, listener, ...Args);                     " +
    "            }                                                          " +
    "        }                                                              " +
    "                                                                       " +
    "    }                                                                  " +
    "                                                                       " +
    "   MySendBeacon( url, data )                                  " +
    "   {                                                                   " +
    "       console.log(  'MySendBeacon',                                   " +
    "                      { 'url' : url },                                 " +
    "                      { 'data' : data } );                             " +
    "   }                                                                   " +
    "                                                                       " +
    "   globalThis.navigator.sendBeacon = MySendBeacon;                         " +
    "                                                                       " +
    "   globalThis.GlobalCounter       = 0;                                      " +
    "   globalThis.GlobalSeenObjects   = {};                                        " +
    "                                                                           " +
    "   class MyTestClass {}                                                    " +
    "                                                                                   " +
    "   MyTestObject1 = new MyTestClass();                                                     " +
    "   MyTestObject2 = new MyTestClass();                                                       " +
    "   MyTestObject3 = new MyTestClass();                                                      " +
    "   MyTestObject4 = new MyTestClass();                                                       " +    
    "                                                                                            " +
    #"    function AddToSeenProtoTypes( ProtoTypeObject, ProtoTypeMetaData ) {                                             " + 
    #"        if ( !( ProtoTypeObject in GlobalSeenObjects )) {                                 " +
    #"            GlobalSeenObjects[ProtoTypeObject] = ProtoTypeMetaData;                             " +
    #"            GlobalSeenObjects[ProtoTypeObject]['instances'] = [];  }                      " +
    #"                                                                                            " +
    #"        return true;                                                                           " +
    #"    }                                                                                          " +
    #"                                                                                               " + 
    #"    function AddToSeenInstances( ProtoTypeObject, InstanceObject, InstanceMetaData ) {         " +
    #"        GlobalSeenObjects[ProtoTypeObject]['instances'].push( InstanceObject ); " +
    #"        return true;                                                                         " +
    #"    }                                                                                          " +
    "                                                                                               " +
    "                                                                                               " + 
    "    IsSeenProtoType( ProtoTypeObject ) {                   " + 
    "        if ( ProtoTypeObject in GlobalSeenObjects ) {                                  " + 
    "            return true;                                                               " + 
    "        }                                                                              " + 
    "        else {                                                                         " + 
    "            return false;                                                              " + 
    "        }                                                                              " + 
    "    }                                                                                  " + 
    "                                                                                       " + 
    "                                                                                       " + 
    "    IsSeenInstance( ProtoTypeObject, InstanceObject ) {                             " + 
    "        if ( ProtoTypeObject in GlobalSeenObjects ) {                          " + 
    "            if ( InstanceObject in GlobalSeenObjects[ProtoTypeObject] ) {         " + 
    "                return true;                                                           " + 
    "            }                                                                          " + 
    "            else {                                                                     " + 
    "                return false;                                                          " + 
    "            }                                                                          " + 
    "        }                                                                              " + 
    "        else {                                                                         " + 
    "            return false;                                                              " + 
    "        }                                                                              " + 
    "    }                                                                                 " + 
    "                                                                       " +
    "                                                                       " +
    "                                                                       " +
    "    addAllEventsListener( window, (evt) =>                             " +
    "    {                                                                  " +
    "        console.log(   'EventObjects',                                 " +
    "                       evt,                                            " +
    "                       evt.target,                                     " +
    "                       {'DOMEventType' : evt.type},                    " +
    "                       {'TargetName' : Object(evt.target)},            " +
    "                       {'TargetProto' : evt.target.__proto__},         " +
    "                       {'TargetTagName' : evt.target.tagName},         " +
    "                       {'TargetText' : evt.target.textContent},        " +
    "                       {'EventError' : JSON.stringify(evt.error)},     " +
    "                       {'EventMessage' : JSON.stringify(evt.data)},    " +
    "                       {'TargetClassName' : evt.target.className} );   " +
    "    }, false )                                                        " +
    "                                                                       " +
    "    addAllEventsListener( document, (evt) =>                           " +
    "    {                                                                  " +
    "        console.log(   'EventObjects',                                 " +
    "                       evt,                                            " +
    "                       evt.target,                                     " +
    "                       {'DOMEventType' : evt.type},                    " +
    "                       {'TargetName' : Object(evt.target)},            " +
    "                       {'TargetProto' : evt.target.__proto__},         " +
    "                       {'TargetTagName' : evt.target.tagName},         " +
    "                       {'TargetText' : evt.target.textContent},        " +
    "                       {'EventError' : JSON.stringify(evt.error)},     " +
    "                       {'EventMessage' : JSON.stringify(evt.data)},    " +
    "                       {'TargetClassName' : evt.target.className} );   " +
    "    }, false )                                                        " +
    "                                                                       " +
    "                                                                       " +
    "                                                                       " )


'''
   "name": "Symbol(Symbol.hasInstance)",
   "value": {
    "type": "function",
    "className": "Function",
    "description": "function [Symbol.hasInstance]() { [native code] }",
    "objectId": "-6696074167990547411.2.634"
   },
   "writable": false,
   "configurable": false,
   "enumerable": false,
   "isOwn": false,
   "symbol": {
    "type": "symbol",
    "description": "Symbol(Symbol.hasInstance)",
    "objectId": "-6696074167990547411.2.635"
   }
  },
'''

# Object.keys(my_object)
# console.log(JSON.parse(JSON.stringify(Event)));


'''
/**
 * Get the keys of the paramaters of a function.
 *
 * @param {function} method  Function to get parameter keys for
 * @return {array}
 */
var STRIP_COMMENTS = /((\/\/.*$)|(\/\*[\s\S]*?\*\/))/mg;
var ARGUMENT_NAMES = /(?:^|,)\s*([^\s,=]+)/g;
function getFunctionParameters ( func ) {
    var fnStr = func.toString().replace(STRIP_COMMENTS, '');
    var argsList = fnStr.slice(fnStr.indexOf('(')+1, fnStr.indexOf(')'));
    var result = argsList.match( ARGUMENT_NAMES );

    if(result === null) {
        return [];
    }
    else {
        var stripped = [];
        for ( var i = 0; i < result.length; i++  ) {
            stripped.push( result[i].replace(/[\s,]/g, '') );
        }
        return stripped;
    }
}
'''