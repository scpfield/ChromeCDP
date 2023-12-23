import sys, os, subprocess, requests, json


#  chrome://process-internals
#  chrome://extensions
#  chrome://version
#  chrome://flags
#  chrome://components
#  chrome://web-app-internals
#  chrome://tracing
#  chrome://memory-internals
#  chrome://support-tool
#  chrome://chrome-urls/



class ChromeLauncher():
    
    def __init__( self, HostName = 'localhost', Port = 9222 ):

        self.HostName       = HostName
        self.Port           = Port
        self.Process        = None
        self.DefaultArgs    = [
                            f' --expose-internals-for-testing',
                        #    f' --aggressive-cache-discard',
                            f' --force-renderer-accessibility',
                            f' --allow-external-pages',
                            f' --allow-legacy-extension-manifests',
                            f' --allow-sandbox-debugging',
                            f' --allow-insecure-localhost',
                            f' --allow-external-pages',
                            f' --enable-begin-frame-control',
                        #    f' --allow-pre-commit-input',
                            f' --allow-profiles-outside-user-dir',
                            f' --allow-unchecked-dangerous-downloads',
                            f' --allow-running-insecure-content',
                            f' --attribution-reporting-debug-mode',
                        #    f' --content-shell-devtools-tab-target',
                        #    f' --content-shell-host-window-size=800x600',
                            f' --silent-debugger-extension-api',
                            f' --bypass-app-banner-engagement-checks',
                        #    f' --browser-test',
                        #    f' --touch-events=enabled',
                        #    f' --enable-pepper-testing',
                        #    f' --ppapi',
                            f' --mojo-is-broker',
                        #    f' --ppapi-in-process',
                        #    f' --debug-devtools',
                        #    f' --debug-devtools-frontend',
                            f' --force-renderer-accessibility',
                        #    f' --debug-packed-apps',
                        #    f' --deterministic-mode',
                            f' --disable-back-forward-cache',
                            f' --disable-background-networking',
                #            f' --disable-background-timer-throttling',
                            f' --disable-backgrounding-occluded-windows',
                        #    f' --disable-breakpad',
                            f' --disable-client-side-phishing-detection',
                            f' --disable-component-update',
                        #    f' --disable-domain-reliability',
                #            f' --disable-external-intent-requests',
                #            f' --disable-features=IntensiveWakeUpThrottling,PaintHolding,ScriptStreaming,IsolateOrigins,ImprovedCookieControls,OptimizationHints,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,AllowAllSitesToInitiateMirroring,AutofillServerCommunication,AutofillUpstream,BackForwardCache,BlockInsecureDownloads,CalculateNativeWinOcclusion,CastAllowAllIPs,DropInputEventsBeforeFirstPaint,IsolateSandboxedIframes,PWAsDefaultOfflinePage,StrictOriginIsolation,WebAssemblyExperimentalJSPI,WebAssemblyLazyCompilation,WebPaymentsExperimentalFeatures,WebShare,AutoExpandDetailsElement,InterestFeedContentSuggestions',
                            f' --disable-hang-monitor',
                #            f' --disable-infobars',
                            f' --disable-input-event-activation-protection',
                            f' --disable-ipc-flooding-protection',
                            f' --disable-lazy-loading',
                            f' --disable-notifications',
                            f' --disable-partial-raster',
                            f' --disable-popup-blocking',
                            f' --disable-prompt-on-repost',
                            f' --enable-experimental-extension-apis'
                #            f' --disable-renderer-backgrounding',
                            f' --disable-site-isolation-trials',
                            f' --enable-renderer-mojo-channel',
                            f' --enable-unsafe-es3-apis',
                #            f' --enable-pepper-testing',
                            f' --disable-sync',
                            f' --disable-web-security',
                #            f' --enable-aggressive-domstorage-flushing',
                #            f' --enable-automation',
                #            f' --enable-blink-features=DumpRenderTree,WebKitTestRunner,EventSender,AutomationControlled,MojoJS,MojoJSTest,AccessibilityObjectModel,BlinkExtensionChromeOS,FeaturePolicyReporting,FluentScrollbars,HighlightAPI,HighlightPointerEvents,TestFeature',
                #            f' --enable-blink-test-features=DumpRenderTree,WebKitTestRunner,EventSender,AutomationControlled,MojoJS,MojoJSTest,AccessibilityObjectModel,BlinkExtensionChromeOS,FeaturePolicyReporting,FluentScrollbars,HighlightAPI,HighlightPointerEvents,TestFeature',
                #            f' --enable-experimental-ui-automation',
                #            f' --enable-experimental-web-platform-features',
                #            f' --enable-experimental-webkit-features',
                #            f' --enable-experimental-extension-apis',
                #            f' --enable-features=DumpRenderTree,WebKitTestRunner,EventSender,AwaitOptimization,SyntheticPointerActions,NetworkService,NetworkServiceInProcess,ChromeLabs,ExtensionsMenuAccessControl,GlobalMediaControlsCastStartStop,IsolatedWebAppDevMode,JavaScriptExperimentalSharedMemory,RecordWebAppDebugInfo,StorageAccessAPI,V8VmFuture,WebAppManifestImmediateUpdating,WebContentsForceDark,ui-debug-tools',
                #            f' --enable-input',
                            f' --enable-logging="C:\\chrome.log"',
                #            f' --enable-precise-memory-info',
                            f' --enable-smooth-scrolling',
                #            f' --enable-webgpu-developer-features',
                #            f' --enable-experimental-input-view-features',
                #            f' --enable-experimental-web-platform-features',
                            f' --force-device-scale-factor=1.5',
                            f' --force-devtools-available',
                            f' --high-dpi-support=1',
                            f' --ignore-certificate-errors',
                     #       f' --ignore-urlfetcher-cert-requests',
                            f' --js-flags="--expose-gc"',
                            f' --log-level=2',
                     #       f' --metrics-recording-only',
                            f' --no-default-browser-check',
                            f' --no-first-run',
                            f' --no-pings',
                            f' --no-sandbox',
                            f' --no-self-delete',
                            f' --password-store=basic',
                            f' --remote-allow-origins=*',
                            f' --remote-debugging-port=9222',
                            f' --show-component-extension-options',
                 #           f' --single-process',
                #            f' --test-type=browser',
                #            f' --dom-automation',
                #            f' --run-web-tests',
                            f' --unsafely-treat-insecure-origin-as-secure="about:blank,file://,file:///C:/python/sam/main.html,http://localhost,https://localhost,https://localhost:8834/#/"',
                #            f' --use-fake-device-for-media-stream',
                #            f' --use-fake-ui-for-media-stream',
                #            f' --use-mock-keychain',
                            f' --user-data-dir="C:\\temp\\chrome"',
                         #   f' --ipc-dump-directory="c:\\ipc"',
                            f' --v=2',
                            
                            ]

        ...
            
    def Launch( self ):
        
        Command =     [ 'C:\\Users\\Administrator\\AppData\\Local\\ms-playwright\\chromium-1060\\chrome-win\\chrome.exe' ]
        Command.extend( self.DefaultArgs )
        
        try:
            CommandStr = ' '.join( Command )
            print('Launching Chrome: ' + CommandStr )
            self.Process = subprocess.Popen( CommandStr )
            return self.Process
        
        except BaseException as e:
            print(GetExceptionInfo(e))
            return None
        ...

    def GetTargetInfo( self, TargetType = None):
    
        Path = None
        
        match TargetType:
            case 'page'     :   Path = '/json'
            case 'browser'  :   Path = '/json/version'
            case _          :   return None
                
        URL = f'http://{self.HostName}:{self.Port}{Path}'
                        
        print('GetTargetInfo: Making HTTP Request to: ' + URL)                        
        
        try:
        
            Response    =  requests.get( url = URL )
            JSONData    =  None
        
            if not Response.ok:
                print( f'Got bad response code: {Response.code}')
                return None
                
            return Response.json()
                
        except BaseException as e:
            print(GetExceptionInfo(e))
            return None
        ...
    
    def GetPageTargetInfo( self, PageIdx = 0 ):
    
        PageTargets = self.GetTargetInfo('page')
        
        print('Number Of PageTargets: ' + str(len(PageTargets)))
        
        if (( not PageTargets ) or
            ( PageIdx > ( len( PageTargets ) - 1 ))):
                return None
        
        for Item in PageTargets:
            print(json.dumps(Item, indent=1))
            Item['type'] = 'page'
            
        return PageTargets[PageIdx]
        ...
        
    def GetBrowserTargetInfo( self ):
        BrowserTargetInfo = self.GetTargetInfo('browser')
        BrowserTargetInfo['type'] = 'browser'
        print(json.dumps(BrowserTargetInfo, indent=1))
        return BrowserTargetInfo
        ...
    
    ...  # End of ChromeLauncher
    
    
'''
--aggressive-cache-discard
--allow-external-pages
--allow-insecure-localhost
--allow-pre-commit-input
--allow-profiles-outside-user-dir
--allow-ra-in-dev-mode
--allow-running-insecure-content
--attribution-reporting-debug-mode
--bypass-app-banner-engagement-checks
--debug-devtools
--debug-devtools-frontend
--debug-packed-apps
--deterministic-mode
--disable-back-forward-cache
--disable-background-networking
--disable-background-timer-throttling
--disable-backgrounding-occluded-windows
--disable-breakpad
--disable-client-side-phishing-detection
--disable-component-extensions-with-background-pages
--disable-default-apps
--disable-domain-reliability
--disable-external-intent-requests
--disable-features=IntensiveWakeUpThrottling,PaintHolding,ScriptStreaming,IsolateOrigins,ImprovedCookieControls,OptimizationHints,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,AllowAllSitesToInitiateMirroring,AutofillServerCommunication,AutofillUpstream,BackForwardCache,BlockInsecureDownloads,CalculateNativeWinOcclusion,CastAllowAllIPs,DropInputEventsBeforeFirstPaint,IsolateSandboxedIframes,PWAsDefaultOfflinePage,StrictOriginIsolation,WebAssemblyExperimentalJSPI,WebAssemblyLazyCompilation,WebPaymentsExperimentalFeatures,WebShare,AutoExpandDetailsElement,InterestFeedContentSuggestions
--disable-hang-monitor
--disable-infobars
--disable-input-event-activation-protection
--disable-ipc-flooding-protection
--disable-lazy-loading
--disable-notifications
--disable-partial-raster
--disable-popup-blocking
--disable-prompt-on-repost
--disable-renderer-backgrounding
--disable-site-isolation-trials
--disable-sync
--disable-web-security
--enable-aggressive-domstorage-flushing
--enable-automation
--enable-blink-features=MojoJS,MojoJSTest
--enable-blink-features=MojoJS,MojoJSTest,ShadowDOMV0
--enable-blink-test-features=MojoJS,MojoJSTest
--enable-blink-test-features=MojoJS,MojoJSTest,ShadowDOMV0
--enable-experimental-ui-automation
--enable-experimental-web-platform-features
--enable-experimental-webkit-features
--enable-features=AwaitOptimization,SyntheticPointerActions,NetworkService,NetworkServiceInProcess,ChromeLabs,ExtensionsMenuAccessControl,GlobalMediaControlsCastStartStop,IsolatedWebAppDevMode,JavaScriptExperimentalSharedMemory,RecordWebAppDebugInfo,StorageAccessAPI,V8VmFuture,WebAppManifestImmediateUpdating,WebContentsForceDark,ui-debug-tools
--enable-input
--enable-logging=stderr
--enable-precise-memory-info
--enable-smooth-scrolling
--enable-webgpu-developer-features
--expose-internals-for-testing
--extensions-on-chrome-urls
--force-color-profile=srgb
--force-device-scale-factor=1.5
--force-devtools-available
--hide-scrollbars
--high-dpi-support=1
--ignore-certificate-errors
--ignore-urlfetcher-cert-requests
--javascript-harmony
--js-flags="--expose-gc"
--log-level=2
--metrics-recording-only
--no-default-browser-check
--no-first-run
--no-pings
--no-sandbox
--no-self-delete
--password-store=basic
--remote-allow-origins=*
--remote-debugging-port=9222
--show-component-extension-options
--silent-debugger-extension-api
--single-process
--test-type
--unsafely-treat-insecure-origin-as-secure="http://localhost,https://localhost,https://localhost:8834/#/"
--use-fake-device-for-media-stream
--use-fake-ui-for-media-stream
--use-mock-keychain
--user-data-dir="C:\\temp\\chrome"
--v=2
'''