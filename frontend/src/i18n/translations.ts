import type { AppLanguage } from '../types/transit';

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
  | 'reducedMotionDesc';

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
    officialTelemetryDesc: 'All fares, line names, and stops adhere strictly to DMRC, DTC, and Indian Railways tariff charts.',
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
    allCorridorsDesc: 'No signal delays, crowd blocks, or diversions reported across Delhi Metro or DTC lines. Use the Incident Simulator above to test simulated disruption scenarios.',
    affectedStops: 'Affected Stops:',
    lastReported: 'Last reported:',
    planAlternative: 'Plan Alternative Bypass',

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
    reducedMotionDesc: 'Disable 3D scene rotations and micro-animations for low-bandwidth.'
  },
  hi: {
    appName: 'राही',
    appTagline: 'आपका शहर, सहजता से जुड़ा हुआ',
    missionTag: 'मिशन भारत DEV-P05',
    missionDesc: 'मल्टी-मॉडल शहरी गतिशीलता, पूरे भारत में दैनिक यात्रियों के सफर को सुगम और पर्यावरण-अनुकूल बनाती हुई।',
    
    // Nav
    navTitle: 'नेविगेशन',
    navDiscover: 'खोजें (Discover)',
    navPlan: 'यात्रा योजना बनाएं',
    navLive: 'लाइव ट्रांजिट',
    navSaved: 'सुरक्षित मार्ग',
    navAssistant: 'एआई यात्रा सहायक',
    navSettings: 'सेटिंग्स',

    // TopBar
    liveAlerts: 'सक्रिय ट्रांजिट अलर्ट',
    raahiAiButton: 'राही AI',

    // Discover Hero
    heroTitle: 'आपकी अगली यात्रा, हुई अब आसान।',
    heroDesc: 'मेट्रो, इलेक्ट्रिक बस और उपनगरीय रेल का मल्टी-मॉडल नेटवर्क। बिना किसी झंझट के सबसे तेज़, सबसे सस्ते और कम भीड़ वाले मार्गों की तुलना करें।',
    allLinesNormal: 'सभी लाइनें सामान्य',
    serviceAlerts: 'सेवा अलर्ट',
    transitGrid: 'ट्रांजिट ग्रिड',

    // Search
    startingOrigin: 'प्रस्थान स्थान (Origin)',
    targetDestination: 'गंतव्य स्थान (Destination)',
    leaveNow: 'अभी निकलें',
    departAt: 'प्रस्थान समय',
    arriveBy: 'पहुंचने का समय',
    searchJourneys: 'यात्रा खोजें',
    searching: 'मार्ग खोज रहे हैं...',
    originPlaceholder: 'जैसे: राजीव चौक, कश्मीरी गेट...',
    destinationPlaceholder: 'जैसे: साइबर सिटी, नोएडा सेक्टर 62...',

    // Priorities
    routePriorities: 'मार्ग प्राथमिकताएँ',
    prefFastest: 'सबसे तेज़',
    prefCheapest: 'सबसे सस्ता',
    prefLessCrowded: 'कम भीड़',
    prefFewerTransfers: 'कम बदलाव',
    prefLessWalking: 'कम पैदल',
    prefAccessible: 'सुगम्य (Accessible)',
    prefEBus: 'डीटीसी ई-बस',
    prefAutoTaxi: 'ऑटो और टैक्सी',
    prefPinkPass: 'गुलाबी टिकट (महिलाएं मुफ्त)',
    prefMultiTransport: 'मल्टी-ट्रांसपोर्ट (ऑटो + मेट्रो)',

    // 3D Scene
    live3dTransitGrid: 'लाइव 3D ट्रांजिट मॉडल',

    // Frequent Commutes
    frequentCommutes: 'नियमित यात्राएं (Frequent Commutes)',
    oneTapReplan: 'एक-क्लिक में पुनः योजना',
    noSavedJourneys: 'अभी कोई सुरक्षित यात्रा नहीं है',
    noSavedJourneysDesc: 'अपने नियमित कार्यालय या कॉलेज के मार्गों को सुरक्षित करें ताकि लाइव देरी देख सकें और एक क्लिक में पुनः योजना बना सकें।',
    replanNow: 'पुनः योजना बनाएं',
    replanJourney: 'पुनः योजना बनाएं',
    direct: 'सीधा मार्ग (बिना बदले)',
    transfer: 'बदलाव',
    transfers: 'बदलाव',

    // Telemetry Banner
    officialTelemetry: 'आधिकारिक ट्रांजिट टेलीमेट्री डेटा',
    officialTelemetryDesc: 'सभी किराए, लाइन के नाम और स्टेशन DMRC, DTC और भारतीय रेल के आधिकारिक टैरिफ चार्ट के अनुसार हैं।',
    viewSystemStatus: 'सिस्टम स्थिति देखें',

    // Plan Journey View
    modifySearch: '← खोज बदलें',
    saveRoute: 'मार्ग सुरक्षित करें',
    saved: 'सुरक्षित किया गया!',
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
    moderateCrowd: 'सामान्य भीड़',
    highCrowd: 'अधिक भीड़',
    veryHighCrowd: 'अत्यधिक भीड़',
    stepByStepItinerary: 'चरण-दर-चरण यात्रा मार्ग',
    intermediateStops: 'मध्यवर्ती स्टॉप',
    stops: 'स्टॉप',

    // Live Transit View
    liveTransitTitle: 'लाइव ट्रांजिट एवं घटना सूचना',
    liveTransitSubtitle: 'रियल-टाइम टेलीमेट्री, ट्रैक सूचनाएं और भीड़ की लाइव स्थिति:',
    syncActive: 'लाइव सिंक सक्रिय',
    incidentSimulator: 'घटना सिम्युलेटर',
    incidentSimulatorDesc: 'देरी और मौसम के अनुसार रियल-टाइम रूटिंग का परीक्षण करें',
    simulatedBadge: 'डेमो / सिम्युलेशन डेटा',
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
    allCorridorsDesc: 'दिल्ली मेट्रो या डीटीसी पर कोई सिग्नल खराबी या डायवर्सन नहीं है। परीक्षण के लिए ऊपर सिम्युलेटर का उपयोग करें।',
    affectedStops: 'प्रभावित स्टॉप:',
    lastReported: 'अंतिम रिपोर्ट:',
    planAlternative: 'वैकल्पिक मार्ग खोजें',

    // Saved Routes View
    savedCommutesTitle: 'सुरक्षित यात्राएं एवं मार्ग',
    savedCommutesSubtitle: 'दैनिक यात्राओं की एक-क्लिक पुनः योजना और लाइव देरी ट्रैक करने के लिए।',
    addCustomCommute: 'नई यात्रा जोड़ें',
    createFirstCommute: 'अपनी पहली यात्रा जोड़ें',
    saveRegularCommute: 'नियमित यात्रा सुरक्षित करें',
    saveRegularCommuteDesc: 'अपनी नियमित यात्रा को अपने डैशबोर्ड में जोड़ें।',
    commuteLabel: 'यात्रा का नाम',
    commuteLabelPlaceholder: 'जैसे: घर से दफ्तर, सप्ताहांत यात्रा',
    preferredOptimization: 'प्राथमिकता',
    cancel: 'रद्द करें',
    saveCommuteButton: 'सुरक्षित करें',
    remove: 'हटाएं',
    confirmDelete: 'क्या आप हटाना चाहते हैं?',

    // AI Assistant
    aiAssistantTitle: 'राही AI सहायक',
    aiAssistantLangs: 'English • हिन्दी',
    aiWelcome: 'नमस्ते! मैं राही AI हूँ, आपका स्मार्ट यात्रा साथी। आज मैं आपकी यात्रा में क्या मदद कर सकता हूँ?',
    aiFastestChip: '⚡ सबसे तेज़ मार्ग',
    aiCheapestChip: '💰 सबसे कम किराया',
    aiDelaysChip: '⚠️ देरी की जांच',
    aiLessWalkingChip: '🚶 कम पैदल चलना',
    aiInputPlaceholder: 'राही से पूछें (जैसे: \'राजीव चौक से साइबर सिटी कैसे जाएं?\')...',
    aiAnalyzing: 'राही AI मार्गों का विश्लेषण कर रहा है...',

    // Settings
    settingsTitle: 'प्राथमिकताएँ एवं सेटिंग्स',
    settingsSubtitle: 'अभिगम्यता, भाषा और क्षेत्रीय प्राथमिकताओं को कॉन्फ़िगर करें।',
    regionalCity: 'शहर (Regional City)',
    appLanguage: 'एप्लिकेशन भाषा',
    accessibleRouting: 'व्हीलचेयर एवं सुगम्य मार्ग',
    accessibleRoutingDesc: 'लिफ्ट, रैंप और सीढ़ी-मुक्त स्थानांतरण को प्राथमिकता दें।',
    reducedMotionSetting: 'कम एनीमेशन मोड',
    reducedMotionDesc: 'कम बैंडविड्थ पर 3D दृश्य और एनिमेशन को सीमित करें।'
  }
};

export const getTranslation = (lang: AppLanguage, key: TranslationKey): string => {
  return translations[lang]?.[key] || translations.en[key] || key;
};
