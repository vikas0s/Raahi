import type { AppLanguage, CrowdLevel } from '../types/transit';

export type TranslationKey =
  | 'appName'
  | 'appTagline'
  | 'missionTag'
  | 'missionDesc'
  | 'navTitle'
  | 'navDiscover'
  | 'navPlan'
  | 'navLive'
  | 'navSaved'
  | 'navAssistant'
  | 'navSettings'
  | 'liveAlerts'
  | 'raahiAiButton'
  | 'heroTitle'
  | 'heroDesc'
  | 'allLinesNormal'
  | 'serviceAlerts'
  | 'transitGrid'
  | 'startingOrigin'
  | 'targetDestination'
  | 'leaveNow'
  | 'departAt'
  | 'arriveBy'
  | 'searchJourneys'
  | 'searching'
  | 'originPlaceholder'
  | 'destinationPlaceholder'
  | 'routePriorities'
  | 'prefFastest'
  | 'prefCheapest'
  | 'prefLessCrowded'
  | 'prefFewerTransfers'
  | 'prefLessWalking'
  | 'prefAccessible'
  | 'prefEBus'
  | 'prefAutoTaxi'
  | 'prefPinkPass'
  | 'prefMultiTransport'
  | 'live3dTransitGrid'
  | 'frequentCommutes'
  | 'oneTapReplan'
  | 'noSavedJourneys'
  | 'noSavedJourneysDesc'
  | 'replanNow'
  | 'replanJourney'
  | 'direct'
  | 'transfer'
  | 'transfers'
  | 'officialTelemetry'
  | 'officialTelemetryDesc'
  | 'viewSystemStatus'
  | 'modifySearch'
  | 'saveRoute'
  | 'saved'
  | 'availableRoutes'
  | 'clickToInspect'
  | 'totalFare'
  | 'mins'
  | 'walking'
  | 'onTime'
  | 'delay'
  | 'selected'
  | 'selectRouteArrow'
  | 'lowCrowd'
  | 'moderateCrowd'
  | 'highCrowd'
  | 'veryHighCrowd'
  | 'stepByStepItinerary'
  | 'intermediateStops'
  | 'stops'
  | 'liveTransitTitle'
  | 'liveTransitSubtitle'
  | 'syncActive'
  | 'incidentSimulator'
  | 'incidentSimulatorDesc'
  | 'simulatedBadge'
  | 'scenarioYellowLine'
  | 'scenarioYellowLineSub'
  | 'scenarioBus'
  | 'scenarioBusSub'
  | 'scenarioPeak'
  | 'scenarioPeakSub'
  | 'scenarioMonsoon'
  | 'scenarioMonsoonSub'
  | 'resetScenario'
  | 'scenarioPrompt'
  | 'activeAdvisories'
  | 'updatedEvery30s'
  | 'allCorridorsOnSchedule'
  | 'allCorridorsDesc'
  | 'affectedStops'
  | 'lastReported'
  | 'planAlternative'
  | 'savedCommutesTitle'
  | 'savedCommutesSubtitle'
  | 'addCustomCommute'
  | 'createFirstCommute'
  | 'saveRegularCommute'
  | 'saveRegularCommuteDesc'
  | 'commuteLabel'
  | 'commuteLabelPlaceholder'
  | 'preferredOptimization'
  | 'cancel'
  | 'saveCommuteButton'
  | 'remove'
  | 'confirmDelete'
  | 'aiAssistantTitle'
  | 'aiAssistantLangs'
  | 'aiWelcome'
  | 'aiFastestChip'
  | 'aiCheapestChip'
  | 'aiDelaysChip'
  | 'aiLessWalkingChip'
  | 'aiInputPlaceholder'
  | 'aiAnalyzing'
  | 'settingsTitle'
  | 'settingsSubtitle'
  | 'regionalCity'
  | 'appLanguage'
  | 'accessibleRouting'
  | 'accessibleRoutingDesc'
  | 'reducedMotionSetting'
  | 'reducedMotionDesc'
  | 'navRail'
  | 'prefRail'
  | 'railConnectTitle'
  | 'railConnectSubtitle'
  // Added keys for complete localization
  | 'startFromCurrentLoc'
  | 'startFromCurrentLocTitle'
  | 'calculatingItineraries'
  | 'calculatingItinerariesSub'
  | 'noDirectRoutes'
  | 'noDirectRoutesSub'
  | 'cleanTransitImpact'
  | 'savesCarbon'
  | 'ecoVerified'
  | 'pinkPassFree'
  | 'serviceUnavailable'
  | 'transfersCountTooltip'
  | 'walkingTimeTooltip'
  | 'fromLabel'
  | 'toLabel'
  | 'distanceLabel'
  | 'classesLabel'
  | 'liveNTES'
  | 'verifiedTimetable'
  | 'walkingSection'
  | 'intermediateStopsCount'
  | 'mapYou'
  | 'mapTransit'
  | 'mapWalk'
  | 'mapBusGps'
  | 'mapLiveDelhiTransit'
  | 'mapLiveTransitMathura'
  | 'mapLiveTransitMumbai'
  | 'mapLiveTransitBengaluru'
  | 'mapBusesCount'
  | 'mapVehiclesCount'
  | 'mapOtdActive'
  | 'mapMathuraActive'
  | 'mapMumbaiActive'
  | 'mapBengaluruActive'
  | 'mapCenterTooltip'
  | 'mapDetectTooltip'
  | 'mapOriginLabel'
  | 'mapDestLabel'
  | 'catMetroStation'
  | 'catBusStop'
  | 'catRailStation'
  | 'catLandmark'
  | 'catCurrentLocation'
  | 'useCurrentLocationShort'
  | 'locatingShort'
  | 'departureTimeLabel'
  | 'targetArrivalLabel'
  | 'quickAddLabel'
  | 'liveNowLabel'
  | 'swapTooltip'
  | 'chipBestEBus'
  | 'chipNagarSeva'
  | 'chipBmtcEBus'
  | 'chipAutoKaaliPeeli'
  | 'chipSharedTempo'
  | 'chipMeteredAutoCab'
  | 'chipMultiLocalMetro'
  | 'chipMultiTempoTrain'
  | 'chipSuburbanTrain'
  | 'chipWomenConcession'
  | 'preferredLabel'
  | 'savingShort'
  | 'crowdInflow'
  | 'liveTimetableBadge'
  | 'recommendedModeLabel'
  | 'lineLabel'
  | 'itinerariesCalculated'
  | 'citySelectDesc'
  | 'langSelectDesc'
  | 'transitApiTitle'
  | 'activeServices'
  | 'engNotesTitle'
  | 'engNotesDesc';

export const translations: Record<AppLanguage, Record<TranslationKey, string>> = {
  en: {
    appName: 'Raahi',
    appTagline: 'Your City, Effortlessly Connected',
    missionTag: 'MISSION BHARAT DEV-P05',
    missionDesc: 'Multi-modal urban mobility, decarbonizing daily commuter corridors across India.',
    
    // Nav
    navTitle: 'Navigation',
    navDiscover: 'Discover',
    navPlan: 'Plan a Journey',
    navLive: 'Live Transit',
    navRail: 'RailConnect',
    navSaved: 'Saved Routes',
    navAssistant: 'AI Travel Assistant',
    navSettings: 'Settings',

    // TopBar
    liveAlerts: 'Active transit alerts',
    raahiAiButton: 'Raahi AI',

    // Discover Hero
    heroTitle: 'Your next journey, made simpler.',
    heroDesc: 'Multi-modal public transit across Metro, Electric Bus, and Suburban Rail. Compare fastest, cheapest, and least-crowded corridors with zero guesswork.',
    allLinesNormal: 'All Lines Normal',
    serviceAlerts: 'Service Alerts',
    transitGrid: 'Transit Grid',

    // Search
    startingOrigin: 'Starting Origin',
    targetDestination: 'Target Destination',
    leaveNow: 'Leave now',
    departAt: 'Depart at',
    arriveBy: 'Arrive by',
    searchJourneys: 'Search Journeys',
    searching: 'Searching routes...',
    originPlaceholder: 'e.g., Rajiv Chowk, Kashmere Gate...',
    destinationPlaceholder: 'e.g., Cyber City, Noida Sec 62...',
    useCurrentLocationShort: 'Use current location',
    locatingShort: 'Locating...',
    departureTimeLabel: 'Departure Time:',
    targetArrivalLabel: 'Target Arrival:',
    quickAddLabel: 'Quick Add:',
    liveNowLabel: 'Live',
    swapTooltip: 'Swap origin and destination',

    // Priorities
    routePriorities: 'Route Priorities',
    prefFastest: 'Fastest',
    prefCheapest: 'Cheapest',
    prefLessCrowded: 'Less Crowded',
    prefFewerTransfers: 'Fewer Transfers',
    prefLessWalking: 'Less Walking',
    prefAccessible: 'Accessible',
    prefEBus: 'DTC Electric Bus',
    prefAutoTaxi: 'Auto & Taxi',
    prefPinkPass: 'Pink Ticket (Women Free)',
    prefMultiTransport: 'Multi-Transport (Auto + Metro)',
    prefRail: '🚆 Indian Railways',
    railConnectTitle: 'Raahi RailConnect — Indian Railways & Local Trains',
    railConnectSubtitle: 'Direct trains, local EMUs, live delays & platform departure boards',

    // City Preference Chips
    chipBestEBus: 'BEST Electric Bus',
    chipNagarSeva: 'Electric Nagar Seva',
    chipBmtcEBus: 'BMTC Electric Bus',
    chipAutoKaaliPeeli: 'Auto & Kaali-Peeli Taxi',
    chipSharedTempo: 'Shared Tempo & Auto',
    chipMeteredAutoCab: 'Metered Auto & Cab',
    chipMultiLocalMetro: 'Multi-Transport (Local / Metro)',
    chipMultiTempoTrain: 'Multi-Transport (Tempo + Train)',
    chipSuburbanTrain: '🚆 Suburban Local Train',
    chipWomenConcession: 'Women Concession',

    // 3D Scene
    live3dTransitGrid: 'Live 3D Transit Grid',

    // Frequent Commutes
    frequentCommutes: 'Frequent Commutes',
    oneTapReplan: 'One-tap replanning',
    noSavedJourneys: 'No saved journeys yet',
    noSavedJourneysDesc: 'Plan your regular office or college trips and save them to track live delays and replan in one click.',
    replanNow: 'Replan Now',
    replanJourney: 'Replan Journey',
    direct: 'Direct',
    transfer: 'transfer',
    transfers: 'transfers',

    // Telemetry Banner
    officialTelemetry: 'Official Transit Telemetry Grounding',
    officialTelemetryDesc: 'All fares, line names, and stops adhere strictly to Maharashtra Transport Dept, GNCTD, DMRC, BEST, BMTC, and Indian Railways tariff charts.',
    viewSystemStatus: 'View System Status',

    // Plan Journey View
    modifySearch: '← Modify Search Parameters',
    saveRoute: 'Save Route',
    saved: 'Saved!',
    availableRoutes: 'Available Routes',
    clickToInspect: 'Click card to inspect',
    totalFare: 'TOTAL FARE',
    mins: 'MINS',
    walking: 'walk',
    onTime: 'On Time',
    delay: 'delay',
    selected: 'Selected',
    selectRouteArrow: 'Select route →',
    lowCrowd: 'Low crowd',
    moderateCrowd: 'Moderate crowd',
    highCrowd: 'High crowd',
    veryHighCrowd: 'Very High crowd',
    stepByStepItinerary: 'STEP-BY-STEP TRANSIT ITINERARY',
    intermediateStops: 'intermediate stops',
    stops: 'stops',
    startFromCurrentLoc: 'Start from current location',
    startFromCurrentLocTitle: 'Recalculate route starting directly from your live GPS position',
    calculatingItineraries: 'Calculating Transit Itineraries...',
    calculatingItinerariesSub: 'Evaluating Metro, Electric Buses, Shared Tempos & Feeder Autos',
    noDirectRoutes: 'No direct routes found',
    noDirectRoutesSub: 'Try searching another nearby landmark or hub.',
    cleanTransitImpact: 'Clean Transit Impact',
    savesCarbon: 'Saves ~{kg} kg CO₂ emissions',
    ecoVerified: 'Eco Verified',
    pinkPassFree: 'Pink Pass: ₹0 (Free)',
    serviceUnavailable: 'Service currently unavailable',
    transfersCountTooltip: 'Transfers count',
    walkingTimeTooltip: 'Walking time',
    fromLabel: 'From:',
    toLabel: 'To:',
    distanceLabel: 'Distance:',
    classesLabel: 'Classes:',
    liveNTES: '● Live NTES Telemetry',
    verifiedTimetable: '✓ Verified IR Timetable',
    walkingSection: 'Walking Section',
    intermediateStopsCount: '{count} intermediate stops',
    itinerariesCalculated: '{count} transit itineraries calculated • {city} Transit Grid',

    // Map
    mapYou: 'You',
    mapTransit: 'Transit',
    mapWalk: 'Walk',
    mapBusGps: 'Bus GPS',
    mapLiveDelhiTransit: 'Live Delhi Transit (OTD)',
    mapLiveTransitMathura: 'Live Braj Transit (E-Bus & Tempos)',
    mapLiveTransitMumbai: 'Live Mumbai Transit (BEST)',
    mapLiveTransitBengaluru: 'Live Bengaluru Transit (BMTC)',
    mapBusesCount: '{count} buses',
    mapVehiclesCount: '{count} vehicles',
    mapOtdActive: 'OTD Key Active',
    mapMathuraActive: 'Smart City Telemetry Active',
    mapMumbaiActive: 'BEST / Chalo Telemetry Active',
    mapBengaluruActive: 'BMTC Telemetry Active',
    mapCenterTooltip: 'Center map on your current location',
    mapDetectTooltip: 'Detect your current location',
    mapOriginLabel: 'Origin',
    mapDestLabel: 'Destination',

    // Autocomplete Categories
    catMetroStation: 'Metro Station',
    catBusStop: 'Bus Terminal / Stop',
    catRailStation: 'Railway Station',
    catLandmark: 'Landmark / Hub',
    catCurrentLocation: 'Current Location',

    // Live Transit View
    liveTransitTitle: 'Live Transit & Incident Awareness',
    liveTransitSubtitle: 'Real-time telemetry, trackside notifications, and crowd density across',
    syncActive: 'Real-time Sync Active',
    incidentSimulator: 'Incident Simulator',
    incidentSimulatorDesc: 'Test real-time routing adaptation against simulated delays & weather',
    simulatedBadge: 'SIMULATED / DEMO DATA',
    scenarioYellowLine: 'Yellow Line Delay',
    scenarioYellowLineSub: '+14m signal calibration',
    scenarioBus: 'DTC Bus Diversion',
    scenarioBusSub: '+20m Ring Road block',
    scenarioPeak: 'Peak Hour Surge',
    scenarioPeakSub: 'Concourse crowd surge',
    scenarioMonsoon: 'Monsoon Rain',
    scenarioMonsoonSub: 'Slow road, Metro priority',
    resetScenario: 'Reset Scenario',
    scenarioPrompt: 'Click any scenario to see real-time route reranking.',
    activeAdvisories: 'Active Service Advisories',
    updatedEvery30s: 'Updated every 30 seconds',
    allCorridorsOnSchedule: 'All transit corridors operating on schedule',
    allCorridorsDesc: 'No signal delays, crowd blocks, or diversions reported across lines. Use the Incident Simulator above to test simulated disruption scenarios.',
    affectedStops: 'Affected Stops:',
    lastReported: 'Last reported:',
    planAlternative: 'Plan Alternative Bypass',
    crowdInflow: 'Crowd Inflow:',
    liveTimetableBadge: 'LIVE TIMETABLE',
    recommendedModeLabel: 'Recommended:',
    lineLabel: 'Line:',

    // Saved Routes View
    savedCommutesTitle: 'Saved Commutes & Routes',
    savedCommutesSubtitle: 'Persisted journeys for one-click replanning and live delay difference tracking.',
    addCustomCommute: 'Add Custom Commute',
    createFirstCommute: 'Create Your First Commute',
    saveRegularCommute: 'Save a Regular Commute',
    saveRegularCommuteDesc: 'Add your frequent transit journey to your personal dashboard.',
    commuteLabel: 'Commute Label',
    commuteLabelPlaceholder: 'e.g., Home to Office, Weekend to NDLS',
    preferredOptimization: 'Preferred Optimization',
    cancel: 'Cancel',
    saveCommuteButton: 'Save Commute',
    remove: 'Remove',
    confirmDelete: 'Confirm delete?',
    preferredLabel: 'Preferred:',
    savingShort: 'Saving...',

    // AI Assistant
    aiAssistantTitle: 'Raahi AI Assistant',
    aiAssistantLangs: 'English • हिन्दी',
    aiWelcome: 'Namaste! I am Raahi AI, your smart local transit companion. How can I help with your journey today?',
    aiFastestChip: '⚡ Fastest Route',
    aiCheapestChip: '💰 Lowest Fare',
    aiDelaysChip: '⚠️ Delays',
    aiLessWalkingChip: '🚶 Less Walking',
    aiInputPlaceholder: 'Ask Raahi (e.g., \'Rajiv Chowk se Cyber City kaise jaye?\')...',
    aiAnalyzing: 'Raahi AI is analyzing transit routes...',

    // Settings
    settingsTitle: 'Preferences & System Settings',
    settingsSubtitle: 'Configure accessibility, language, and regional preferences.',
    regionalCity: 'Regional City',
    appLanguage: 'Application Language',
    accessibleRouting: 'Wheelchair & Accessibility Routing',
    accessibleRoutingDesc: 'Prioritize lifts, ramps, wide gates, and step-free transfers.',
    reducedMotionSetting: 'Reduced Motion',
    reducedMotionDesc: 'Disable 3D scene rotations and micro-animations for low-bandwidth.',
    citySelectDesc: 'Select the active metropolitan public transport network.',
    langSelectDesc: 'Support for English and Hindi (हिन्दी).',
    transitApiTitle: 'Transit API Credentials & Fare Calculation Engines',
    activeServices: '3 Active Services',
    engNotesTitle: 'MISSION BHARAT DEV-P05 Engineering Notes',
    engNotesDesc: 'Raahi is designed to minimize multi-modal commuter friction across Indian megacities. All simulated alerts are transparently designated as [SIMULATED] to preserve data integrity.'
  },
  hi: {
    appName: 'राही',
    appTagline: 'आपका शहर, सहजता से जुड़ा हुआ',
    missionTag: 'मिशन भारत DEV-P05',
    missionDesc: 'मल्टी-मॉडल शहरी गतिशीलता, पूरे भारत में दैनिक यात्रियों के सफर को सुगम और पर्यावरण-अनुकूल बनाती हुई।',
    
    // Nav
    navTitle: 'नेविगेशन',
    navDiscover: 'खोजें',
    navPlan: 'यात्रा की योजना बनाएँ',
    navLive: 'लाइव सार्वजनिक परिवहन',
    navRail: 'रेल कनेक्ट',
    navSaved: 'सहेजे गए मार्ग',
    navAssistant: 'एआई यात्रा सहायक',
    navSettings: 'सेटिंग्स',

    // TopBar
    liveAlerts: 'सक्रिय ट्रांजिट सूचनाएं',
    raahiAiButton: 'राही AI',

    // Discover Hero
    heroTitle: 'आपकी अगली यात्रा, हुई अब आसान।',
    heroDesc: 'मेट्रो, इलेक्ट्रिक बस और उपनगरीय रेल का मल्टी-मॉडल नेटवर्क। बिना किसी झंझट के सबसे तेज़, सबसे सस्ते और कम भीड़ वाले मार्गों की तुलना करें।',
    allLinesNormal: 'सभी लाइनें सामान्य रूप से संचालित',
    serviceAlerts: 'सेवा अलर्ट',
    transitGrid: 'ट्रांजिट नेटवर्क',

    // Search
    startingOrigin: 'प्रारंभिक स्थान',
    targetDestination: 'गंतव्य',
    leaveNow: 'अभी निकलें',
    departAt: 'प्रस्थान समय',
    arriveBy: 'पहुंचने का समय',
    searchJourneys: 'यात्राएँ खोजें',
    searching: 'मार्ग खोजे जा रहे हैं...',
    originPlaceholder: 'जैसे: राजीव चौक, कश्मीरी गेट...',
    destinationPlaceholder: 'जैसे: साइबर सिटी, नोएडा सेक्टर 62...',
    useCurrentLocationShort: 'वर्तमान स्थान का उपयोग करें',
    locatingShort: 'स्थान खोज रहे हैं...',
    departureTimeLabel: 'प्रस्थान समय:',
    targetArrivalLabel: 'पहुंचने का समय:',
    quickAddLabel: 'त्वरित समय जोड़ें:',
    liveNowLabel: 'लाइव',
    swapTooltip: 'प्रारंभिक स्थान और गंतव्य आपस में बदलें',

    // Priorities
    routePriorities: 'मार्ग प्राथमिकताएँ',
    prefFastest: 'सबसे तेज़',
    prefCheapest: 'सबसे किफायती',
    prefLessCrowded: 'कम भीड़',
    prefFewerTransfers: 'कम बदलाव',
    prefLessWalking: 'कम पैदल चलना',
    prefAccessible: 'सुगम्य (व्हीलचेयर अनुकूल)',
    prefEBus: 'डीटीसी इलेक्ट्रिक बस',
    prefAutoTaxi: 'ऑटो व टैक्सी',
    prefPinkPass: 'गुलाबी टिकट (महिलाओं के लिए मुफ्त)',
    prefMultiTransport: 'मल्टी-ट्रांसपोर्ट (ऑटो + मेट्रो)',
    prefRail: '🚆 भारतीय रेल / लोकल ट्रेन',
    railConnectTitle: 'राही रेल कनेक्ट — भारतीय रेलवे व लोकल ट्रेन',
    railConnectSubtitle: 'सीधी ट्रेनें, ईएमयू लोकल, लाइव रनिंग स्टेटस और प्लेटफार्म बोर्ड',

    // City Preference Chips
    chipBestEBus: 'बेस्ट इलेक्ट्रिक बस',
    chipNagarSeva: 'इलेक्ट्रिक नगर सेवा',
    chipBmtcEBus: 'बीएमटीसी इलेक्ट्रिक बस',
    chipAutoKaaliPeeli: 'ऑटो व काली-पीली टैक्सी',
    chipSharedTempo: 'शेयरिंग टेम्पो व ऑटो',
    chipMeteredAutoCab: 'मीटर ऑटो व कैब',
    chipMultiLocalMetro: 'मल्टी-ट्रांसपोर्ट (लोकल / मेट्रो)',
    chipMultiTempoTrain: 'मल्टी-ट्रांसपोर्ट (टेम्पो + ट्रेन)',
    chipSuburbanTrain: '🚆 उपनगरीय लोकल ट्रेन',
    chipWomenConcession: 'महिला रियायत (छूट)',

    // 3D Scene
    live3dTransitGrid: 'लाइव 3D ट्रांजिट मॉडल',

    // Frequent Commutes
    frequentCommutes: 'नियमित यात्राएँ',
    oneTapReplan: 'एक क्लिक में पुनः योजना',
    noSavedJourneys: 'अभी कोई सहेजी गई यात्रा नहीं है',
    noSavedJourneysDesc: 'अपने नियमित कार्यालय या कॉलेज के मार्गों को सहेजें ताकि लाइव देरी देख सकें और एक क्लिक में पुनः योजना बना सकें।',
    replanNow: 'पुनः योजना बनाएँ',
    replanJourney: 'पुनः योजना बनाएँ',
    direct: 'सीधा मार्ग',
    transfer: 'बदलाव',
    transfers: 'बदलाव',

    // Telemetry Banner
    officialTelemetry: 'आधिकारिक ट्रांजिट टेलीमेट्री डेटा',
    officialTelemetryDesc: 'सभी किराए, लाइन के नाम और स्टेशन महाराष्ट्र परिवहन विभाग, GNCTD, BEST, DMRC, BMTC और भारतीय रेल के आधिकारिक टैरिफ चार्ट के अनुसार हैं।',
    viewSystemStatus: 'सिस्टम स्थिति देखें',

    // Plan Journey View
    modifySearch: '← खोज के विकल्प बदलें',
    saveRoute: 'मार्ग सहेजें',
    saved: 'सहेज लिया गया!',
    availableRoutes: 'उपलब्ध मार्ग',
    clickToInspect: 'विवरण देखने के लिए कार्ड पर क्लिक करें',
    totalFare: 'कुल किराया',
    mins: 'मिनट',
    walking: 'पैदल',
    onTime: 'समय पर',
    delay: 'देरी',
    selected: 'चयनित',
    selectRouteArrow: 'मार्ग चुनें →',
    lowCrowd: 'कम भीड़',
    moderateCrowd: 'मध्यम भीड़',
    highCrowd: 'अधिक भीड़',
    veryHighCrowd: 'अत्यधिक भीड़',
    stepByStepItinerary: 'चरण-दर-चरण यात्रा विवरण',
    intermediateStops: 'मध्यवर्ती स्टॉप',
    stops: 'स्टॉप',
    startFromCurrentLoc: 'वर्तमान स्थान से शुरू करें',
    startFromCurrentLocTitle: 'अपनी लाइव जीपीएस स्थिति से मार्ग की पुनः गणना करें',
    calculatingItineraries: 'यात्रा विकल्पों की गणना हो रही है...',
    calculatingItinerariesSub: 'मेट्रो, इलेक्ट्रिक बस, शेयरिंग टेम्पो और फीडर ऑटो का विश्लेषण जारी...',
    noDirectRoutes: 'कोई सीधा मार्ग नहीं मिला',
    noDirectRoutesSub: 'कृपया किसी अन्य नजदीकी स्टेशन, स्टॉप या लैंडमार्क से खोजें।',
    cleanTransitImpact: 'स्वच्छ हरित यात्रा प्रभाव',
    savesCarbon: 'लगभग ~{kg} किग्रा CO₂ उत्सर्जन की बचत',
    ecoVerified: 'इको प्रमाणित',
    pinkPassFree: 'गुलाबी टिकट: ₹0 (मुफ्त)',
    serviceUnavailable: 'सेवा वर्तमान में उपलब्ध नहीं है',
    transfersCountTooltip: 'बदलावों की संख्या',
    walkingTimeTooltip: 'पैदल चलने का समय',
    fromLabel: 'प्रारंभिक:',
    toLabel: 'गंतव्य:',
    distanceLabel: 'दूरी:',
    classesLabel: 'श्रेणियाँ:',
    liveNTES: '● लाइव NTES टेलीमेट्री',
    verifiedTimetable: '✓ सत्यापित रेलवे समय सारिणी',
    walkingSection: 'पैदल खंड',
    intermediateStopsCount: '{count} मध्यवर्ती स्टॉप',
    itinerariesCalculated: '{count} यात्रा विकल्प उपलब्ध • {city} ट्रांजिट नेटवर्क',

    // Map
    mapYou: 'आप',
    mapTransit: 'सार्वजनिक परिवहन',
    mapWalk: 'पैदल',
    mapBusGps: 'बस जीपीएस',
    mapLiveDelhiTransit: 'लाइव दिल्ली ट्रांजिट (OTD)',
    mapLiveTransitMathura: 'लाइव ब्रज ट्रांजिट (ई-बस व ऑटो)',
    mapLiveTransitMumbai: 'लाइव मुंबई ट्रांजिट (BEST)',
    mapLiveTransitBengaluru: 'लाइव बेंगलुरु ट्रांजिट (BMTC)',
    mapBusesCount: '{count} बसें',
    mapVehiclesCount: '{count} वाहन',
    mapOtdActive: 'OTD सक्रिय',
    mapMathuraActive: 'स्मार्ट सिटी टेलीमेट्री सक्रिय',
    mapMumbaiActive: 'BEST / चलो टेलीमेट्री सक्रिय',
    mapBengaluruActive: 'BMTC टेलीमेट्री सक्रिय',
    mapCenterTooltip: 'मानचित्र को अपने वर्तमान स्थान पर केंद्रित करें',
    mapDetectTooltip: 'वर्तमान स्थान का पता लगाएं',
    mapOriginLabel: 'प्रारंभिक स्थान (A)',
    mapDestLabel: 'गंतव्य स्थान (B)',

    // Autocomplete Categories
    catMetroStation: 'मेट्रो स्टेशन',
    catBusStop: 'बस स्टॉप / टर्मिनल',
    catRailStation: 'रेलवे स्टेशन',
    catLandmark: 'स्थान / लैंडमार्क',
    catCurrentLocation: 'वर्तमान स्थान',

    // Live Transit View
    liveTransitTitle: 'लाइव सार्वजनिक परिवहन एवं घटना सूचना',
    liveTransitSubtitle: 'रियल-टाइम टेलीमेट्री, ट्रैक सूचनाएं और भीड़ की लाइव स्थिति:',
    syncActive: 'लाइव सिंक सक्रिय',
    incidentSimulator: 'घटना सिम्युलेटर',
    incidentSimulatorDesc: 'देरी और मौसम के अनुसार रियल-टाइम रूटिंग का परीक्षण करें',
    simulatedBadge: 'सिम्युलेटेड / डेमो डेटा',
    scenarioYellowLine: 'येलो लाइन देरी',
    scenarioYellowLineSub: '+14 मिनट सिग्नल सुधार',
    scenarioBus: 'डीटीसी बस डायवर्सन',
    scenarioBusSub: '+20 मिनट रिंग रोड जाम',
    scenarioPeak: 'पीक ऑवर भीड़',
    scenarioPeakSub: 'स्टेशनों पर भारी भीड़',
    scenarioMonsoon: 'मानसून बारिश',
    scenarioMonsoonSub: 'सड़कों पर धीमा ट्रैफिक, मेट्रो को प्राथमिकता',
    resetScenario: 'रीसेट करें',
    scenarioPrompt: 'रीयल-टाइम रूट री-रैंकिंग देखने के लिए किसी भी परिदृश्य पर क्लिक करें।',
    activeAdvisories: 'सक्रिय सेवा सूचनाएं',
    updatedEvery30s: 'प्रत्येक 30 सेकंड में अपडेट',
    allCorridorsOnSchedule: 'सभी मार्ग निर्धारित समय पर संचालित',
    allCorridorsDesc: 'सभी ट्रांजिट मार्गों पर सेवाएं सुचारू रूप से चल रही हैं। किसी भी देरी का परीक्षण करने के लिए ऊपर सिम्युलेटर का उपयोग करें।',
    affectedStops: 'प्रभावित स्टॉप:',
    lastReported: 'अंतिम रिपोर्ट:',
    planAlternative: 'वैकल्पिक मार्ग खोजें',
    crowdInflow: 'भीड़ आगमन:',
    liveTimetableBadge: 'लाइव समय सारिणी',
    recommendedModeLabel: 'सुझाया गया साधन:',
    lineLabel: 'लाइन:',

    // Saved Routes View
    savedCommutesTitle: 'सहेजे गए मार्ग एवं दैनिक यात्राएँ',
    savedCommutesSubtitle: 'दैनिक यात्राओं की एक-क्लिक में पुनः योजना और लाइव देरी ट्रैक करने के लिए।',
    addCustomCommute: 'नया मार्ग जोड़ें',
    createFirstCommute: 'अपनी पहली यात्रा सहेजें',
    saveRegularCommute: 'नियमित यात्रा सहेजें',
    saveRegularCommuteDesc: 'अपनी नियमित यात्रा को अपने डैशबोर्ड में सहेजें।',
    commuteLabel: 'यात्रा का नाम',
    commuteLabelPlaceholder: 'जैसे: घर से कार्यालय, सप्ताहांत यात्रा',
    preferredOptimization: 'प्राथमिकता',
    cancel: 'रद्द करें',
    saveCommuteButton: 'सुरक्षित करें',
    remove: 'हटाएँ',
    confirmDelete: 'क्या आप हटाना चाहते हैं?',
    preferredLabel: 'प्राथमिकता:',
    savingShort: 'सहेजा जा रहा है...',

    // AI Assistant
    aiAssistantTitle: 'राही AI सहायक',
    aiAssistantLangs: 'English • हिन्दी',
    aiWelcome: 'नमस्ते! मैं राही AI हूँ, आपका स्मार्ट यात्रा साथी। आज मैं आपकी यात्रा में क्या सहायता कर सकता हूँ?',
    aiFastestChip: '⚡ सबसे तेज़ मार्ग',
    aiCheapestChip: '💰 सबसे कम किराया',
    aiDelaysChip: '⚠️ देरी की जांच',
    aiLessWalkingChip: '🚶 कम पैदल चलना',
    aiInputPlaceholder: 'राही से पूछें (जैसे: \'राजीव चौक से साइबर सिटी कैसे जाएँ?\')...',
    aiAnalyzing: 'राही AI मार्गों का विश्लेषण कर रहा है...',

    // Settings
    settingsTitle: 'प्राथमिकताएँ एवं सिस्टम सेटिंग्स',
    settingsSubtitle: 'अभिगम्यता, भाषा और क्षेत्रीय प्राथमिकताओं को कॉन्फ़िगर करें।',
    regionalCity: 'शहर / क्षेत्रीय नेटवर्क',
    appLanguage: 'एप्लिकेशन भाषा',
    accessibleRouting: 'व्हीलचेयर एवं सुगम्य मार्ग',
    accessibleRoutingDesc: 'लिफ्ट, रैंप और सीढ़ी-मुक्त स्थानांतरण को प्राथमिकता दें।',
    reducedMotionSetting: 'कम एनीमेशन मोड',
    reducedMotionDesc: 'कम बैंडविड्थ पर 3D दृश्य और एनिमेशन को सीमित करें।',
    citySelectDesc: 'सक्रिय महानगर सार्वजनिक परिवहन नेटवर्क चुनें।',
    langSelectDesc: 'अंग्रेजी और हिन्दी भाषा का समर्थन।',
    transitApiTitle: 'ट्रांजिट एपीआई क्रेडेंशियल एवं किराया गणना इंजन',
    activeServices: '3 सक्रिय सेवाएं',
    engNotesTitle: 'मिशन भारत DEV-P05 इंजीनियरिंग विवरण',
    engNotesDesc: 'राही को भारतीय महानगरों में दैनिक यात्रा को सरल और सुगम बनाने के लिए तैयार किया गया है। डेटा प्रामाणिकता के लिए सभी नकली अलर्ट को [सिम्युलेटेड] के रूप में चिन्हित किया गया है।'
  }
};

export const getTranslation = (lang: AppLanguage, key: TranslationKey): string => {
  return translations[lang]?.[key] || translations.en[key] || key;
};

// Route Tag Localizer
const ROUTE_TAG_TRANSLATIONS: Record<string, string> = {
  'Fastest': 'सबसे तेज़',
  'Lowest Fare': 'सबसे किफायती',
  'Least Crowded': 'कम भीड़',
  'Direct Cab': 'डायरेक्ट कैब / टैक्सी',
  'Govt Metered Auto': 'सरकारी मीटर ऑटो',
  'Govt Metered Taxi': 'सरकारी मीटर टैक्सी',
  'Direct Reserved Auto': 'आरक्षित ऑटो',
  'Shared Tempo': 'शेयरिंग टेम्पो',
  'Shared Tempo & Auto': 'शेयरिंग टेम्पो व ऑटो',
  'Most Popular': 'सर्वाधिक लोकप्रिय',
  'Green Electric Bus': 'हरित इलेक्ट्रिक बस',
  'DTC Electric Bus': 'डीटीसी इलेक्ट्रिक बस',
  'BEST Electric Bus': 'बेस्ट इलेक्ट्रिक बस',
  'BMTC Electric Bus': 'बीएमटीसी इलेक्ट्रिक बस',
  'Electric Nagar Seva': 'इलेक्ट्रिक नगर सेवा',
  'Private Taxi (Limited)': 'प्राइवेट टैक्सी (सीमित)',
  'Metro Closed': 'मेट्रो सेवा बंद',
  'Metro (Alternative)': 'मेट्रो (वैकल्पिक मार्ग)',
  'Multi-Transport (Auto + Metro)': 'मल्टी-ट्रांसपोर्ट (ऑटो + मेट्रो)',
  'Multi-Transport (E-Rickshaw + Metro)': 'मल्टी-ट्रांसपोर्ट (ई-रिक्शा + मेट्रो)',
  'Multi-Transport (Braj Feeder)': 'मल्टी-ट्रांसपोर्ट (ब्रज फीडर)',
  'Multi-Transport (Local / Metro)': 'मल्टी-ट्रांसपोर्ट (लोकल / मेट्रो)',
  'Multi-Transport (Tempo + Train)': 'मल्टी-ट्रांसपोर्ट (टेम्पो + ट्रेन)',
  'Short Distance Recommended': 'कम दूरी हेतु उत्तम',
  'Local E-Rickshaw Hop': 'लोकल ई-रिक्शा',
  'Mumbai Suburban Local': 'मुंबई उपनगरीय लोकल',
  'Maha Mumbai Metro': 'महा मुंबई मेट्रो',
  'Namma Metro': 'नम्मा मेट्रो'
};

export function localizeRouteTag(tag: string, lang: AppLanguage): string {
  if (lang !== 'hi') return tag;
  if (ROUTE_TAG_TRANSLATIONS[tag]) return ROUTE_TAG_TRANSLATIONS[tag];
  if (tag.startsWith('🚆')) {
    return tag.replace('Suburban Local Train', 'उपनगरीय लोकल ट्रेन').replace('Indian Railways', 'भारतीय रेल');
  }
  return tag;
}

// Transport Mode Localizer
const MODE_TRANSLATIONS: Record<string, string> = {
  walk: 'पैदल',
  metro: 'मेट्रो',
  bus: 'बस',
  ebus: 'इलेक्ट्रिक बस',
  auto: 'ऑटो',
  taxi: 'टैक्सी',
  'e-rickshaw': 'ई-रिक्शा',
  rail: 'ट्रेन / रेलवे',
  ferry: 'फेरी'
};

export function localizeMode(mode: string, lang: AppLanguage): string {
  if (lang !== 'hi') return mode;
  return MODE_TRANSLATIONS[mode.toLowerCase()] || mode;
}

// Autocomplete Category Localizer
const CATEGORY_TRANSLATIONS: Record<string, string> = {
  metro_station: 'मेट्रो स्टेशन',
  bus_terminal: 'बस टर्मिनल',
  bus_stop: 'बस स्टॉप',
  rail_station: 'रेलवे स्टेशन',
  railway_station: 'रेलवे स्टेशन',
  landmark: 'स्थान / लैंडमार्क',
  hub: 'ट्रांजिट हब',
  current_location: 'वर्तमान स्थान'
};

export function localizeCategory(category: string, lang: AppLanguage): string {
  if (lang !== 'hi') return category.replace('_', ' ');
  return CATEGORY_TRANSLATIONS[category.toLowerCase()] || category.replace('_', ' ');
}

// Crowd Level Localizer
export function localizeCrowdLevel(level: CrowdLevel, lang: AppLanguage): string {
  if (lang !== 'hi') return `${level} crowd`;
  switch (level) {
    case 'Low':
      return 'कम भीड़';
    case 'Moderate':
      return 'मध्यम भीड़';
    case 'High':
      return 'अधिक भीड़';
    case 'Very High':
      return 'अत्यधिक भीड़';
    default:
      return `${level} भीड़`;
  }
}
