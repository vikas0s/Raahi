import React, { useState, useEffect } from 'react';
import {
  Train,
  Clock,
  MapPin,
  Calendar,
  Search,
  Radio,
  ArrowRight,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import {
  getTrainsBetweenStations,
  getLiveTrainStatus,
  getStationLiveBoard,
  getTrainSchedule
} from '../../services/api';
import type {
  TrainSummary,
  LiveRunningStatus,
  StationBoardItem,
  TrainSchedule
} from '../../types/transit';

interface Props {
  selectedCity: string;
  onSelectTrainForJourney?: (fromStation: string, toStation: string) => void;
}

type HubTab = 'between' | 'live' | 'board';

interface CityRailConfig {
  defaultFrom: string;
  defaultTo: string;
  defaultBoard: string;
  defaultLiveTrain: string;
  networkTitle: string;
  networkBadge: string;
  networkSubtitle: string;
  popularStations: Array<{ code: string; name: string; region: string }>;
  quickCorridors: Array<{ from: string; to: string; label: string }>;
  quickPresets: Array<{ no: string; name: string }>;
}

const CITY_RAIL_CONFIGS: Record<string, CityRailConfig> = {
  'mumbai': {
    defaultFrom: 'CCG',
    defaultTo: 'BVI',
    defaultBoard: 'CSMT',
    defaultLiveTrain: '99001',
    networkTitle: 'Mumbai Suburban Railway Network',
    networkBadge: 'Western · Central · Harbour Lines',
    networkSubtitle: 'Lifeline of Mumbai — High-frequency suburban commuter EMU services carrying 7.5M+ daily passengers.',
    popularStations: [
      { code: 'CCG', name: 'Churchgate (Western Terminal)', region: 'Mumbai' },
      { code: 'CSMT', name: 'CSMT (Central/Harbour Terminus)', region: 'Mumbai' },
      { code: 'DDR', name: 'Dadar (Western & Central Interchange)', region: 'Mumbai' },
      { code: 'BVI', name: 'Borivali (Western Fast Corridor)', region: 'Mumbai' },
      { code: 'ADH', name: 'Andheri (Western & Metro Line 1)', region: 'Mumbai' },
      { code: 'TNA', name: 'Thane (Central Main Line & Trans-Harbour)', region: 'Mumbai' },
      { code: 'KYN', name: 'Kalyan Jn (Central Trunk)', region: 'Mumbai' },
      { code: 'VSH', name: 'Vashi (Harbour Line / Navi Mumbai)', region: 'Mumbai' },
      { code: 'PNVL', name: 'Panvel (Harbour Line Terminal)', region: 'Mumbai' }
    ],
    quickCorridors: [
      { from: 'CCG', to: 'BVI', label: 'Churchgate ➔ Borivali (WR Fast)' },
      { from: 'CSMT', to: 'TNA', label: 'CSMT ➔ Thane (CR Fast)' },
      { from: 'CSMT', to: 'PNVL', label: 'CSMT ➔ Panvel (Harbour)' },
      { from: 'DDR', to: 'KYN', label: 'Dadar ➔ Kalyan (CR Fast)' }
    ],
    quickPresets: [
      { no: '99001', name: 'Churchgate - Borivali Fast Local' },
      { no: '99002', name: 'CSMT - Kalyan Fast Local' },
      { no: '99003', name: 'CSMT - Panvel Harbour Local' },
      { no: '99004', name: 'Churchgate - Virar AC Local' },
      { no: '99005', name: 'Dadar - Thane Slow Local' }
    ]
  },
  'bengaluru': {
    defaultFrom: 'SBC',
    defaultTo: 'WFD',
    defaultBoard: 'SBC',
    defaultLiveTrain: '06551',
    networkTitle: 'Bengaluru Commuter Rail Network (SWR)',
    networkBadge: 'South Western Railway Commuter MEMU',
    networkSubtitle: 'Suburban MEMU/DEMU services connecting Majestic, Whitefield, Yesvantpur, and tech corridors at flat ₹10–₹25.',
    popularStations: [
      { code: 'SBC', name: 'KSR Bengaluru City (Majestic)', region: 'Bengaluru' },
      { code: 'BNC', name: 'Bengaluru Cantt', region: 'Bengaluru' },
      { code: 'BYPL', name: 'Baiyyappanahalli (Purple Metro Link)', region: 'Bengaluru' },
      { code: 'WFD', name: 'Whitefield (Kadugodi Tech Corridor)', region: 'Bengaluru' },
      { code: 'YPR', name: 'Yesvantpur Junction (Green Metro Link)', region: 'Bengaluru' },
      { code: 'BAND', name: 'Banaswadi', region: 'Bengaluru' },
      { code: 'CRLM', name: 'Karmelaram (Sarjapur / ORR Link)', region: 'Bengaluru' },
      { code: 'HSRA', name: 'Hosur (Interstate Commuter)', region: 'Bengaluru' }
    ],
    quickCorridors: [
      { from: 'SBC', to: 'WFD', label: 'KSR Bengaluru ➔ Whitefield (SWR MEMU)' },
      { from: 'YPR', to: 'BYPL', label: 'Yesvantpur ➔ Baiyyappanahalli' },
      { from: 'SBC', to: 'HSRA', label: 'KSR Bengaluru ➔ Hosur' },
      { from: 'WFD', to: 'BNC', label: 'Whitefield ➔ Bengaluru Cantt' }
    ],
    quickPresets: [
      { no: '06551', name: 'SBC - Whitefield Commuter MEMU' },
      { no: '06593', name: 'Yesvantpur - Baiyyappanahalli MEMU' },
      { no: '06591', name: 'KSR Bengaluru - Hosur Commuter' },
      { no: '06552', name: 'Whitefield - KSR Bengaluru MEMU' }
    ]
  },
  'delhi': {
    defaultFrom: 'NDLS',
    defaultTo: 'GZB',
    defaultBoard: 'NDLS',
    defaultLiveTrain: '04408',
    networkTitle: 'Delhi NCR Suburban & Ring Railway',
    networkBadge: 'Northern Railway Suburban EMUs',
    networkSubtitle: 'Unreserved suburban EMUs along Ghaziabad, Palwal, Shakurbasti, plus the 35-km Ring Railway loop.',
    popularStations: [
      { code: 'NDLS', name: 'New Delhi (Yellow & Airport Metro)', region: 'Delhi NCR' },
      { code: 'NZM', name: 'Hazrat Nizamuddin (Pink Metro Link)', region: 'Delhi NCR' },
      { code: 'DLI', name: 'Old Delhi Jn (Chandni Chowk)', region: 'Delhi NCR' },
      { code: 'GZB', name: 'Ghaziabad Junction', region: 'Delhi NCR' },
      { code: 'FDB', name: 'Faridabad (Violet Metro Link)', region: 'Delhi NCR' },
      { code: 'SOJ', name: 'Sarojini Nagar (Ring Railway)', region: 'Delhi NCR' },
      { code: 'LPN', name: 'Lajpat Nagar (Ring Railway & Metro)', region: 'Delhi NCR' },
      { code: 'TKJ', name: 'Tilak Bridge (Suburban Hub)', region: 'Delhi NCR' }
    ],
    quickCorridors: [
      { from: 'NDLS', to: 'GZB', label: 'New Delhi ➔ Ghaziabad (EMU)' },
      { from: 'NZM', to: 'NDLS', label: 'Nizamuddin ➔ New Delhi (EMU Trunk)' },
      { from: 'SOJ', to: 'LPN', label: 'Sarojini Nagar ➔ Lajpat Nagar (Ring Rail)' },
      { from: 'FDB', to: 'NDLS', label: 'Faridabad ➔ New Delhi (Southern EMU)' }
    ],
    quickPresets: [
      { no: '04408', name: 'Delhi - Ghaziabad Suburban EMU' },
      { no: '04415', name: 'Delhi Ring Railway Circular Local' },
      { no: '04422', name: 'Palwal - New Delhi Suburban EMU' },
      { no: '12002', name: 'NDLS - Bhopal Shatabdi Express' },
      { no: '12280', name: 'Taj Express Superfast' }
    ]
  },
  'mathura': {
    defaultFrom: 'MTJ',
    defaultTo: 'BDB',
    defaultBoard: 'MTJ',
    defaultLiveTrain: '04419',
    networkTitle: 'Braj Heritage & Regional Rail Network',
    networkBadge: 'Heritage Rail Bus & NCR Commuter',
    networkSubtitle: 'Mathura-Vrindavan Heritage Rail Bus (#04419/#04420) & regional commuter passenger shuttles at flat ₹10.',
    popularStations: [
      { code: 'MTJ', name: 'Mathura Junction', region: 'Mathura & Vrindavan' },
      { code: 'BDB', name: 'Vrindavan (Heritage Rail Bus)', region: 'Mathura & Vrindavan' },
      { code: 'MRT', name: 'Mathura Cantt', region: 'Mathura & Vrindavan' },
      { code: 'BTSR', name: 'Bhuteshwar', region: 'Mathura & Vrindavan' },
      { code: 'CHJ', name: 'Chhata Commuter Halt', region: 'Mathura & Vrindavan' },
      { code: 'KSV', name: 'Kosi Kalan', region: 'Mathura & Vrindavan' }
    ],
    quickCorridors: [
      { from: 'MTJ', to: 'BDB', label: 'Mathura Jn ➔ Vrindavan (Heritage Rail Bus)' },
      { from: 'MTJ', to: 'KSV', label: 'Mathura Jn ➔ Kosi Kalan (Commuter Shuttle)' },
      { from: 'BTSR', to: 'MTJ', label: 'Bhuteshwar ➔ Mathura Jn' }
    ],
    quickPresets: [
      { no: '04419', name: 'Mathura - Vrindavan Rail Bus' },
      { no: '04420', name: 'Vrindavan - Mathura Rail Bus' },
      { no: '04408', name: 'Mathura - NDLS EMU Local' },
      { no: '14212', name: 'NDLS - Agra Intercity' },
      { no: '12280', name: 'Taj Express Superfast' }
    ]
  }
};

function getCityConfig(city: string): CityRailConfig {
  const c = city.toLowerCase();
  if (c.includes('mumbai') || c.includes('bombay')) return CITY_RAIL_CONFIGS['mumbai'];
  if (c.includes('bengaluru') || c.includes('bangalore')) return CITY_RAIL_CONFIGS['bengaluru'];
  if (c.includes('mathura') || c.includes('vrindavan') || c.includes('braj')) return CITY_RAIL_CONFIGS['mathura'];
  return CITY_RAIL_CONFIGS['delhi'];
}

export const RailConnectHub: React.FC<Props> = ({ selectedCity, onSelectTrainForJourney }) => {
  const [activeTab, setActiveTab] = useState<HubTab>('between');

  const cityConfig = getCityConfig(selectedCity);

  // Trains Between Stations State
  const [fromCode, setFromCode] = useState<string>(cityConfig.defaultFrom);
  const [toCode, setToCode] = useState<string>(cityConfig.defaultTo);
  const [travelDate, setTravelDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [trains, setTrains] = useState<TrainSummary[]>([]);
  const [isSearchingTrains, setIsSearchingTrains] = useState<boolean>(false);
  const [dataSource, setDataSource] = useState<string>('verified_schedule');
  const [expandedTrainSchedule, setExpandedTrainSchedule] = useState<Record<string, TrainSchedule | null>>({});
  const [loadingSchedule, setLoadingSchedule] = useState<Record<string, boolean>>({});

  // Live Running Status State
  const [searchTrainNo, setSearchTrainNo] = useState<string>(cityConfig.defaultLiveTrain);
  const [liveStatus, setLiveStatus] = useState<LiveRunningStatus | null>(null);
  const [isFetchingLive, setIsFetchingLive] = useState<boolean>(false);

  // Live Station Board State
  const [boardStation, setBoardStation] = useState<string>(cityConfig.defaultBoard);
  const [boardItems, setBoardItems] = useState<StationBoardItem[]>([]);
  const [isFetchingBoard, setIsFetchingBoard] = useState<boolean>(false);

  // Update state whenever selectedCity changes
  useEffect(() => {
    const cfg = getCityConfig(selectedCity);
    setFromCode(cfg.defaultFrom);
    setToCode(cfg.defaultTo);
    setBoardStation(cfg.defaultBoard);
    setSearchTrainNo(cfg.defaultLiveTrain);

    // Fetch trains between default stations for city
    setIsSearchingTrains(true);
    getTrainsBetweenStations(cfg.defaultFrom, cfg.defaultTo, travelDate)
      .then(res => {
        setTrains(res.trains);
        setDataSource(res.data_source);
      })
      .catch(err => console.error('Failed to search trains on city change:', err))
      .finally(() => setIsSearchingTrains(false));

    // Fetch live status for city's signature train
    setIsFetchingLive(true);
    getLiveTrainStatus(cfg.defaultLiveTrain, travelDate)
      .then(setLiveStatus)
      .catch(err => console.error('Failed to fetch live status:', err))
      .finally(() => setIsFetchingLive(false));

    // Fetch station board for city's hub
    setIsFetchingBoard(true);
    getStationLiveBoard(cfg.defaultBoard, 4)
      .then(res => setBoardItems(res.departures))
      .catch(err => console.error('Failed to fetch station board:', err))
      .finally(() => setIsFetchingBoard(false));
  }, [selectedCity]);

  // Search trains between stations
  const handleSearchTrains = async () => {
    if (!fromCode || !toCode) return;
    setIsSearchingTrains(true);
    try {
      const res = await getTrainsBetweenStations(fromCode, toCode, travelDate);
      setTrains(res.trains);
      setDataSource(res.data_source);
    } catch (err) {
      console.error('Failed to search trains:', err);
    } finally {
      setIsSearchingTrains(false);
    }
  };

  // Fetch live running status
  const handleFetchLiveStatus = async (trainNo?: string) => {
    const target = trainNo || searchTrainNo;
    if (!target) return;
    setIsFetchingLive(true);
    try {
      const res = await getLiveTrainStatus(target, travelDate);
      setLiveStatus(res);
    } catch (err) {
      console.error('Failed to get live status:', err);
    } finally {
      setIsFetchingLive(false);
    }
  };

  // Fetch station live board
  const handleFetchStationBoard = async (stCode?: string) => {
    const target = stCode || boardStation;
    if (!target) return;
    setIsFetchingBoard(true);
    try {
      const res = await getStationLiveBoard(target, 4);
      setBoardItems(res.departures);
    } catch (err) {
      console.error('Failed to fetch station board:', err);
    } finally {
      setIsFetchingBoard(false);
    }
  };

  // Toggle timetable inspection for a specific train
  const toggleTrainSchedule = async (trainNo: string) => {
    if (expandedTrainSchedule[trainNo]) {
      setExpandedTrainSchedule(prev => ({ ...prev, [trainNo]: null }));
      return;
    }
    setLoadingSchedule(prev => ({ ...prev, [trainNo]: true }));
    try {
      const sched = await getTrainSchedule(trainNo);
      setExpandedTrainSchedule(prev => ({ ...prev, [trainNo]: sched }));
    } catch (err) {
      console.error('Failed to load train schedule:', err);
    } finally {
      setLoadingSchedule(prev => ({ ...prev, [trainNo]: false }));
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* RailConnect Header Card */}
      <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 sm:p-6 shadow-[0_2px_14px_rgba(41,45,41,0.04)]">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-[#8B1E1E]/12 border border-[#8B1E1E]/25 flex items-center justify-center text-[#8B1E1E] shadow-xs shrink-0">
              <Train size={26} className="stroke-[2.2]" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="font-heading font-extrabold text-2xl text-[#1F231F] tracking-tight">
                  {cityConfig.networkTitle}
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide bg-[#8B1E1E]/12 text-[#8B1E1E] border border-[#8B1E1E]/25">
                  {cityConfig.networkBadge}
                </span>
              </div>
              <p className="text-xs text-[#52544D] font-medium mt-1">
                {cityConfig.networkSubtitle}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-xl bg-[#EEECE3] text-[#253D30] border border-[#D8D4C7]">
            <ShieldCheck size={15} className="text-[#4E7C5F] stroke-[2.5]" />
            <span>{dataSource === 'railradar_live' ? 'RailRadar Live API' : 'Verified IR Timetables'}</span>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 mt-6 p-1.5 rounded-xl bg-[#EEECE3]/70 border border-[#D8D4C7] overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab('between')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'between'
                ? 'bg-[#8B1E1E] text-white shadow-xs'
                : 'text-[#454841] hover:text-[#1F231F] hover:bg-[#FFFEFA]'
            }`}
          >
            <Train size={14} />
            <span>Trains Between Stations</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('live')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'live'
                ? 'bg-[#8B1E1E] text-white shadow-xs'
                : 'text-[#454841] hover:text-[#1F231F] hover:bg-[#FFFEFA]'
            }`}
          >
            <Radio size={14} className={activeTab === 'live' ? 'animate-pulse' : ''} />
            <span>Live Running Status</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('board')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'board'
                ? 'bg-[#8B1E1E] text-white shadow-xs'
                : 'text-[#454841] hover:text-[#1F231F] hover:bg-[#FFFEFA]'
            }`}
          >
            <Clock size={14} />
            <span>Station Departure Board</span>
          </button>
        </div>
      </div>

      {/* TAB 1: TRAINS BETWEEN STATIONS */}
      {activeTab === 'between' && (
        <div className="space-y-5">
          {/* Search Controls Card */}
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.03)] space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
              <div className="sm:col-span-4">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-[#52544D] mb-1.5">
                  Departure Station
                </label>
                <select
                  value={fromCode}
                  onChange={(e) => setFromCode(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#D8D4C7] bg-[#FFFEFA] text-xs font-bold text-[#1F231F] focus:outline-none focus:ring-2 focus:ring-[#8B1E1E]"
                >
                  {cityConfig.popularStations.map((s) => (
                    <option key={s.code} value={s.code}>
                      {s.name} ({s.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-4">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-[#52544D] mb-1.5">
                  Arrival Station
                </label>
                <select
                  value={toCode}
                  onChange={(e) => setToCode(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#D8D4C7] bg-[#FFFEFA] text-xs font-bold text-[#1F231F] focus:outline-none focus:ring-2 focus:ring-[#8B1E1E]"
                >
                  {cityConfig.popularStations.map((s) => (
                    <option key={s.code} value={s.code}>
                      {s.name} ({s.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-[#52544D] mb-1.5">
                  Date
                </label>
                <input
                  type="date"
                  value={travelDate}
                  onChange={(e) => setTravelDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#D8D4C7] bg-[#FFFEFA] text-xs font-bold text-[#1F231F] focus:outline-none focus:ring-2 focus:ring-[#8B1E1E]"
                />
              </div>

              <div className="sm:col-span-2">
                <button
                  type="button"
                  onClick={handleSearchTrains}
                  disabled={isSearchingTrains}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-[#8B1E1E] text-white hover:bg-[#721818] transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50"
                >
                  <Search size={14} className="stroke-[2.5]" />
                  <span>{isSearchingTrains ? 'Finding...' : 'Find Trains'}</span>
                </button>
              </div>
            </div>

            {/* Quick Route Shortcuts for selectedCity */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#D8D4C7]/60 text-xs">
              <span className="font-bold text-[#52544D] text-[11px]">Popular Corridors:</span>
              {cityConfig.quickCorridors.map((c, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setFromCode(c.from);
                    setToCode(c.to);
                    getTrainsBetweenStations(c.from, c.to, travelDate).then(res => {
                      setTrains(res.trains);
                      setDataSource(res.data_source);
                    });
                  }}
                  className="px-2.5 py-1 rounded-lg bg-[#EEECE3] hover:bg-[#E3DFD4] font-bold text-[#253D30] border border-[#D8D4C7] cursor-pointer"
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Trains Results Feed */}
          <div className="space-y-3.5">
            <div className="flex items-center justify-between">
              <h3 className="font-heading font-bold text-base text-[#1F231F]">
                Available Trains ({trains.length})
              </h3>
              <span className="text-xs font-semibold text-[#52544D]">
                {fromCode} → {toCode}
              </span>
            </div>

            {trains.length === 0 ? (
              <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-8 text-center space-y-2">
                <p className="font-heading font-bold text-base text-[#1F231F]">No direct trains found between these stations</p>
                <p className="text-xs text-[#52544D]">Try switching stations from the popular corridors above.</p>
              </div>
            ) : (
              trains.map((t) => {
                const sched = expandedTrainSchedule[t.train_number];
                const isLoadingSched = loadingSchedule[t.train_number];

                return (
                  <div
                    key={t.train_number}
                    className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.03)] hover:border-[#8B1E1E]/50 transition-all text-left"
                  >
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 mb-3">
                      <div>
                        <div className="flex items-center gap-2.5">
                          <span className="px-2 py-0.5 rounded-md text-xs font-mono font-extrabold bg-[#8B1E1E]/12 text-[#8B1E1E] border border-[#8B1E1E]/25">
                            #{t.train_number}
                          </span>
                          <h4 className="font-heading font-bold text-base text-[#1F231F]">
                            {t.train_name}
                          </h4>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-[#EEECE3] text-[#454841] border border-[#D8D4C7]">
                            {t.train_type}
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-[#52544D] mt-1">
                          Runs: {t.running_days.join(', ')} • Distance: {t.distance_km} km • {t.halts_count} intermediate halts
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                          t.live_delay_mins > 0
                            ? 'bg-[#BD4F44]/15 text-[#882218] border-[#BD4F44]/30'
                            : 'bg-[#5B8A6E]/15 text-[#253D30] border-[#5B8A6E]/30'
                        }`}>
                          {t.live_status}
                        </span>
                      </div>
                    </div>

                    {/* Schedule strip */}
                    <div className="grid grid-cols-3 gap-2 py-3 px-4 rounded-xl bg-[#EEECE3]/60 border border-[#D8D4C7] mb-3 text-center">
                      <div className="text-left">
                        <p className="font-heading font-extrabold text-lg text-[#1F231F]">{t.departure_time}</p>
                        <p className="text-xs font-bold text-[#52544D]">{t.origin_name} ({t.origin_code})</p>
                        {t.platform_origin && (
                          <span className="text-[10px] font-bold text-[#8B1E1E]">PF {t.platform_origin}</span>
                        )}
                      </div>

                      <div className="flex flex-col items-center justify-center">
                        <span className="text-xs font-bold text-[#52544D]">{t.duration_minutes}m</span>
                        <div className="w-full flex items-center gap-1 my-1">
                          <div className="h-0.5 w-full bg-[#8B1E1E]/40" />
                          <ArrowRight size={12} className="text-[#8B1E1E] shrink-0" />
                        </div>
                        <span className="text-[10px] text-[#52544D]">Direct Service</span>
                      </div>

                      <div className="text-right">
                        <p className="font-heading font-extrabold text-lg text-[#1F231F]">{t.arrival_time}</p>
                        <p className="text-xs font-bold text-[#52544D]">{t.destination_name} ({t.destination_code})</p>
                        {t.platform_dest && (
                          <span className="text-[10px] font-bold text-[#8B1E1E]">PF {t.platform_dest}</span>
                        )}
                      </div>
                    </div>

                    {/* Classes & Fares */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                      <div className="flex flex-wrap items-center gap-2">
                        {Object.entries(t.fares).map(([cls, fare]) => (
                          <span
                            key={cls}
                            className="px-2.5 py-1 rounded-lg bg-[#EEECE3] font-bold text-xs text-[#1F231F] border border-[#D8D4C7]"
                          >
                            <span className="text-[#52544D] mr-1">{cls}:</span>
                            <span className="text-[#8B1E1E]">₹{Math.round(fare)}</span>
                          </span>
                        ))}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => toggleTrainSchedule(t.train_number)}
                          className="px-3 py-1.5 rounded-xl border border-[#D8D4C7] bg-[#FFFEFA] hover:bg-[#EEECE3] text-xs font-bold text-[#253D30] transition-all cursor-pointer flex items-center gap-1.5"
                        >
                          <Layers size={13} />
                          <span>{sched ? 'Hide Halts' : 'View Timetable'}</span>
                          {sched ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                        </button>

                        {onSelectTrainForJourney && (
                          <button
                            type="button"
                            onClick={() => onSelectTrainForJourney(t.origin_name, t.destination_name)}
                            className="px-3 py-1.5 rounded-xl bg-[#8B1E1E] hover:bg-[#721818] text-white text-xs font-bold transition-all cursor-pointer shadow-xs"
                          >
                            Plan Journey
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Expandable Timetable / Halts */}
                    {sched && (
                      <div className="mt-4 pt-4 border-t border-[#D8D4C7] space-y-2">
                        <h5 className="font-heading font-bold text-xs text-[#1F231F] uppercase tracking-wider">
                          Intermediate Halts & Platform Telemetry:
                        </h5>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
                          {sched.halts.map((h, hIdx) => (
                            <div key={hIdx} className="p-2.5 rounded-xl bg-[#EEECE3]/60 border border-[#D8D4C7] text-xs">
                              <p className="font-bold text-[#1F231F]">{h.station_name} ({h.station_code})</p>
                              <p className="text-[11px] text-[#52544D] mt-0.5">
                                Arr: {h.arrival_time} • Dep: {h.departure_time}
                              </p>
                              <p className="text-[10px] text-[#8B1E1E] font-semibold">{h.platform || 'Platform 1'}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* TAB 2: LIVE RUNNING STATUS */}
      {activeTab === 'live' && (
        <div className="space-y-5">
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.03)] space-y-4">
            <div className="flex flex-col sm:flex-row items-center gap-3">
              <div className="flex-1 w-full">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-[#52544D] mb-1.5">
                  Train Number or Name
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchTrainNo}
                    onChange={(e) => setSearchTrainNo(e.target.value)}
                    placeholder="Enter 5-digit Train Number, e.g. 99001 or 04419"
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-[#D8D4C7] bg-[#FFFEFA] text-xs font-bold text-[#1F231F] focus:outline-none focus:ring-2 focus:ring-[#8B1E1E]"
                  />
                  <Train size={16} className="absolute left-3 top-3 text-[#52544D]" />
                </div>
              </div>

              <div className="w-full sm:w-auto self-end">
                <button
                  type="button"
                  onClick={() => handleFetchLiveStatus()}
                  disabled={isFetchingLive}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold bg-[#8B1E1E] text-white hover:bg-[#721818] transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50"
                >
                  <Radio size={14} className={isFetchingLive ? 'animate-pulse' : ''} />
                  <span>{isFetchingLive ? 'Tracking...' : 'Track Live Status'}</span>
                </button>
              </div>
            </div>

            {/* Presets for selectedCity */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#D8D4C7]/60 text-xs">
              <span className="font-bold text-[#52544D] text-[11px]">Quick Track:</span>
              {cityConfig.quickPresets.map((p) => (
                <button
                  key={p.no}
                  type="button"
                  onClick={() => {
                    setSearchTrainNo(p.no);
                    handleFetchLiveStatus(p.no);
                  }}
                  className={`px-2.5 py-1 rounded-lg font-bold text-xs border cursor-pointer transition-all ${
                    searchTrainNo === p.no
                      ? 'bg-[#8B1E1E] text-white border-[#8B1E1E]'
                      : 'bg-[#EEECE3] hover:bg-[#E3DFD4] text-[#253D30] border-[#D8D4C7]'
                  }`}
                >
                  #{p.no} {p.name}
                </button>
              ))}
            </div>
          </div>

          {/* Live Status Card */}
          {liveStatus && (
            <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-6 shadow-[0_2px_14px_rgba(41,45,41,0.04)] space-y-5 text-left">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-[#D8D4C7]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-md text-sm font-mono font-extrabold bg-[#8B1E1E]/12 text-[#8B1E1E] border border-[#8B1E1E]/25">
                      #{liveStatus.train_number}
                    </span>
                    <h3 className="font-heading font-extrabold text-xl text-[#1F231F]">
                      {liveStatus.train_name}
                    </h3>
                  </div>
                  <p className="text-xs text-[#52544D] font-medium mt-1">
                    Telemetry Source: {liveStatus.data_source === 'railradar_live' ? 'RailRadar Real-Time NTES Feed' : 'Verified Timetable Estimation'}
                  </p>
                </div>

                <div className={`px-3.5 py-1.5 rounded-full text-xs font-bold border flex items-center gap-2 ${
                  liveStatus.delay_minutes > 0
                    ? 'bg-[#BD4F44]/15 text-[#882218] border-[#BD4F44]/30'
                    : 'bg-[#5B8A6E]/15 text-[#253D30] border-[#5B8A6E]/30'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${liveStatus.delay_minutes > 0 ? 'bg-[#BD4F44]' : 'bg-[#5B8A6E] animate-ping'}`} />
                  <span>{liveStatus.delay_minutes > 0 ? `Delayed by ${liveStatus.delay_minutes} mins` : 'Operating On Time'}</span>
                </div>
              </div>

              {/* Main Metric Banner */}
              <div className="p-4 rounded-xl bg-[#EEECE3]/60 border border-[#D8D4C7] grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <p className="text-[11px] font-bold uppercase tracking-wider text-[#52544D]">Current Location</p>
                  <p className="font-heading font-bold text-base text-[#1F231F] mt-0.5">{liveStatus.current_station}</p>
                  <p className="text-xs text-[#304B3C] font-semibold">{liveStatus.current_status}</p>
                </div>

                <div>
                  <p className="text-[11px] font-bold uppercase tracking-wider text-[#52544D]">Next Approaching Station</p>
                  <p className="font-heading font-bold text-base text-[#1F231F] mt-0.5">{liveStatus.next_station || 'En Route'}</p>
                  <p className="text-xs text-[#52544D] font-medium">ETA: {liveStatus.eta_destination}</p>
                </div>

                <div>
                  <p className="text-[11px] font-bold uppercase tracking-wider text-[#52544D]">Live Speed & Telemetry</p>
                  <p className="font-heading font-bold text-base text-[#8B1E1E] mt-0.5">
                    {liveStatus.speed_kmh ? `${liveStatus.speed_kmh} km/h` : 'Station Halt'}
                  </p>
                  <p className="text-xs text-[#52544D] font-mono">Updated: {liveStatus.last_reported_time || 'Just now'}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: STATION DEPARTURE BOARD */}
      {activeTab === 'board' && (
        <div className="space-y-5">
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.03)] space-y-3">
            <div className="flex flex-col sm:flex-row items-center gap-3">
              <div className="flex-1 w-full">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-[#52544D] mb-1.5">
                  Select Railway Station
                </label>
                <select
                  value={boardStation}
                  onChange={(e) => {
                    setBoardStation(e.target.value);
                    handleFetchStationBoard(e.target.value);
                  }}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#D8D4C7] bg-[#FFFEFA] text-xs font-bold text-[#1F231F] focus:outline-none focus:ring-2 focus:ring-[#8B1E1E]"
                >
                  {cityConfig.popularStations.map((s) => (
                    <option key={s.code} value={s.code}>
                      {s.name} ({s.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="w-full sm:w-auto self-end">
                <button
                  type="button"
                  onClick={() => handleFetchStationBoard()}
                  disabled={isFetchingBoard}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-[#8B1E1E] text-white hover:bg-[#721818] transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50"
                >
                  <Clock size={14} />
                  <span>{isFetchingBoard ? 'Refreshing...' : 'Refresh Board'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Board Table */}
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.03)]">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#D8D4C7]">
              <div>
                <h3 className="font-heading font-bold text-lg text-[#1F231F]">
                  Live Station Departure Board: {boardStation}
                </h3>
                <p className="text-xs text-[#52544D] font-medium">
                  Trains scheduled to arrive or depart within the next 4 hours
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#EEECE3] text-[#253D30] border border-[#D8D4C7]">
                Live Board Sync
              </span>
            </div>

            {boardItems.length === 0 ? (
              <p className="text-xs text-[#52544D] text-center py-6">No scheduled departures in this lookahead window.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-[#D8D4C7] text-[#52544D] font-bold text-[11px]">
                      <th className="py-2.5 px-3">Train # & Name</th>
                      <th className="py-2.5 px-3">Destination</th>
                      <th className="py-2.5 px-3">Scheduled</th>
                      <th className="py-2.5 px-3">Expected</th>
                      <th className="py-2.5 px-3">Platform</th>
                      <th className="py-2.5 px-3 text-right">Running Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {boardItems.map((item, idx) => (
                      <tr key={idx} className="border-b border-[#EEECE3] hover:bg-[#EEECE3]/40">
                        <td className="py-2.5 px-3">
                          <span className="font-mono font-bold text-[#8B1E1E]">#{item.train_number}</span>{' '}
                          <span className="font-bold text-[#1F231F]">{item.train_name}</span>
                          <span className="block text-[10px] text-[#52544D]">{item.train_type}</span>
                        </td>
                        <td className="py-2.5 px-3 font-semibold text-[#1F231F]">{item.destination_name}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-[#52544D]">{item.scheduled_time}</td>
                        <td className="py-2.5 px-3 font-mono font-extrabold text-[#1F231F]">{item.expected_time}</td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded-md font-bold bg-[#8B1E1E]/12 text-[#8B1E1E] border border-[#8B1E1E]/25">
                            {item.platform}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold border ${
                            item.delay_minutes > 0
                              ? 'bg-[#BD4F44]/15 text-[#882218] border-[#BD4F44]/30'
                              : 'bg-[#5B8A6E]/15 text-[#253D30] border-[#5B8A6E]/30'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
