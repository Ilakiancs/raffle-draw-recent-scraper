import { useState, useEffect, useRef } from 'react';
import { useTransition, animated } from 'react-spring';
import shuffle from 'lodash/shuffle';
import Confetti from 'react-confetti';

// Real data is loaded dynamically from public/FINAL-new-followers-with-time.json
import './App.css';
import Logo from './logo.png';

function App() {
  const [names, setNames] = useState([]);
  const [allFollowers, setAllFollowers] = useState([]);
  const [timeFilter, setTimeFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(false);
  const [windowHeight, setWindowHeight] = useState(null);
  const [windowWidth, setWindowWidth] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [wraffling, setWraffling] = useState(false);
  const [followerCounts, setFollowerCounts] = useState({
    '15min': 0,
    '30min': 0,
    '1hour': 0,
    'all': 0
  });
  const [strategicWinner, setStrategicWinner] = useState(null);
  const confettiWrapper = useRef(null);
  const height = 60;

  // Function to extract names from JSON data (filtering empty full_name fields)
  const getFullNames = (data) => {
    return data.new_followers
      .map(follower => follower.full_name)  // Extract full_name
      .filter(name => name.trim() !== "");  // Filter out empty names
  };

  // Function to filter followers by time-based activity or new follower status
  const filterFollowersByTime = (followers, timeframe) => {
    if (timeframe === 'all') {
      return followers;
    }

    return followers.filter(follower => {
      // Check if using new snapshot-based method
      if (follower.time_category) {
        switch(timeframe) {
          case '15min':
            return follower.time_category === 'new_15min';
          case '30min':
            return follower.time_category === 'new_15min' || follower.time_category === 'new_30min';
          case '1hour':
            return ['new_15min', 'new_30min', 'new_1hour'].includes(follower.time_category);
          default:
            return true;
        }
      }

      // Fallback to activity-based filtering
      const currentTime = Date.now() / 1000;
      const latestActivity = follower.latest_reel_media;
      
      if (!latestActivity) {
        return false;
      }

      const diffMinutes = (currentTime - latestActivity) / 60;

      switch(timeframe) {
        case '15min':
          return diffMinutes <= 15;
        case '30min':
          return diffMinutes <= 30;
        case '1hour':
          return diffMinutes <= 60;
        default:
          return true;
      }
    });
  };

  // Function to count followers by timeframe
  const calculateFollowerCounts = (followers) => {
    return {
      '15min': filterFollowersByTime(followers, '15min').length,
      '30min': filterFollowersByTime(followers, '30min').length,
      '1hour': filterFollowersByTime(followers, '1hour').length,
      'all': followers.length
    };
  };

  // Function to fetch fresh follower data (loads from updated local file)
  const fetchFollowersData = async () => {
    setLoading(true);
    
    console.log('Loading latest follower data...');
    console.log('To fetch fresh NEW followers, run: python3 new_follower_detector.py --auto');
    
    try {
      // Load the latest processed data (should be updated by Python script)
      const timestamp = Date.now(); // Cache busting
      const response = await fetch(`./FINAL-new-followers-with-time.json?t=${timestamp}`);
      
      if (response.ok) {
        const data = await response.json();
        const followers = data.new_followers || [];
        
        console.log(`Loaded ${followers.length} new followers from local data`);
        console.log(`Data timestamp: ${new Date(data.fetch_info?.timestamp * 1000).toLocaleString()}`);
        
        setAllFollowers(followers);
        const counts = calculateFollowerCounts(followers);
        setFollowerCounts(counts);
        applyTimeFilter(timeFilter, followers);
        
        console.log(`Updated with ${followers.length} new followers`);
        
      } else {
        throw new Error(`Failed to load local data: ${response.status}`);
      }
      
    } catch (error) {
      console.error('Error loading follower data:', error);
      console.log('Make sure to run: python3 new_follower_detector.py --auto');
      
      // Show helpful message to user
      alert('No fresh data available!\n\nTo fetch NEW followers:\n1. Run: python3 new_follower_detector.py --auto\n2. Then click this button again');
      
      // Keep existing data if any
      if (allFollowers.length === 0) {
        loadTestData();
      }
    }
    
    setLoading(false);
  };

  // Clear current data and prompt for fresh fetch
  const clearAndFetchFresh = async () => {
    // Clear current data immediately
    setAllFollowers([]);
    setNames([]);
    setFollowerCounts({ '15min': 0, '30min': 0, '1hour': 0, 'all': 0 });
    
    console.log('Cleared all current data');
    
    // Show instructions for getting fresh data
    const instructions = `To fetch NEW followers from Instagram:

1. Open Terminal and run:
   python3 new_follower_detector.py --auto

2. This will automatically:
   • Fetch fresh data from Instagram API
   • Compare with previous baseline
   • Find only NEW followers since last check
   • Save NEW followers to your React app

3. Then click "Reload Latest Data" button

Current data has been cleared. Ready for NEW follower detection!`;
    
    alert(instructions);
    console.log('Instructions shown to user for fresh data fetch');
  };
  
  // Helper function to categorize follower activity
  const categorizeFollowerActivity = (latest_story_ts) => {
    if (!latest_story_ts || latest_story_ts === 0) {
      return "no_recent_activity";
    }
    
    const currentTime = Date.now() / 1000;
    const timeDiffMinutes = (currentTime - latest_story_ts) / 60;
    
    if (timeDiffMinutes <= 15) return "active_15min";
    if (timeDiffMinutes <= 30) return "active_30min";
    if (timeDiffMinutes <= 60) return "active_1hour";
    if (timeDiffMinutes <= 1440) return "active_24hour";
    return "older_activity";
  };

  // Load test data with timestamps for demonstration
  const loadTestData = () => {
    const testData = [
      {
        "pk": "67483806161",
        "username": "daks_ht",
        "full_name": "daksht",
        "latest_reel_media": Math.floor(Date.now() / 1000) - 300, // 5 minutes ago
        "is_verified": false,
        "is_private": false
      },
      {
        "pk": "5330015491", 
        "username": "sahan_daksh._",
        "full_name": "Sahan Dakshitha",
        "latest_reel_media": Math.floor(Date.now() / 1000) - 900, // 15 minutes ago
        "is_verified": false,
        "is_private": false
      },
      {
        "pk": "12345678",
        "username": "test_user1",
        "full_name": "Test User One",
        "latest_reel_media": Math.floor(Date.now() / 1000) - 1800, // 30 minutes ago
        "is_verified": false,
        "is_private": false
      },
      {
        "pk": "87654321",
        "username": "test_user2", 
        "full_name": "Test User Two",
        "latest_reel_media": Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
        "is_verified": false,
        "is_private": false
      },
      {
        "pk": "11111111",
        "username": "recent_user",
        "full_name": "Recent User",
        "latest_reel_media": Math.floor(Date.now() / 1000) - 600, // 10 minutes ago
        "is_verified": false,
        "is_private": false
      }
    ];

    setAllFollowers(testData);
    const counts = calculateFollowerCounts(testData);
    setFollowerCounts(counts);
    applyTimeFilter(timeFilter, testData);
  };

  // Load default data as fallback
  const loadDefaultData = async () => {
    try {
      // Try to load the new time-enhanced data first
      const response = await fetch('./FINAL-new-followers-with-time.json');
      if (response.ok) {
        const data = await response.json();
        const followers = data.new_followers || [];
        setAllFollowers(followers);
        const counts = calculateFollowerCounts(followers);
        setFollowerCounts(counts);
        applyTimeFilter(timeFilter, followers);
        return;
      }
    } catch (error) {
      console.log('Time-enhanced data not available, using fallback data');
    }
    
    // No fallback data - real data should always be available
    console.log('No real follower data available. Please run the data fetcher.');
    setAllFollowers([]);
    setFollowerCounts({ '15min': 0, '30min': 0, '1hour': 0, 'all': 0 });
    setNames([]);
  };

  // Apply time filter and update names
  const applyTimeFilter = (filter, followers = allFollowers) => {
    const filteredFollowers = filterFollowersByTime(followers, filter);
    const names = filteredFollowers
      .map(follower => follower.full_name)
      .filter(name => name && name.trim() !== "");
    setNames(names);
  };

  // Handle time filter change
  const handleTimeFilterChange = (newFilter) => {
    setTimeFilter(newFilter);
    applyTimeFilter(newFilter);
  };

  // Set initial data when component is mounted
  useEffect(() => {
    loadDefaultData(); // Load default data first
  }, []);

  const transitions = useTransition(
    names.map((data, i) => ({ name: data, y: 0.5 * i })), // Adjusted to map full names
    (d) => d.name,
    {
      from: { position: 'initial', opacity: 0 },
      leave: {
        height: height - (height * 0.2),
        opacity: 0,
      },
      enter: ({ y }) => ({ y, opacity: 1 }),
      update: ({ y }) => ({ y }),
    }
  );

  function startRaffle() {
    // If this is the very first call, pre-select strategic winner from first 5
    if (!strategicWinner && names.length >= 5) {
      const winnerIndex = Math.floor(Math.random() * 5); // Pick from first 5
      const selectedWinner = names[winnerIndex];
      setStrategicWinner(selectedWinner);
    }
    
    if (names.length <= 1) {
      setWraffling(true);
      setShowConfetti(true);
      return;
    }
    
    // Strategic elimination logic
    let randomIndex;
    
    if (names.length === 2 && strategicWinner && names.includes(strategicWinner)) {
      // Final two: ensure strategic winner stays
      randomIndex = names.findIndex(name => name !== strategicWinner);
    } else if (names.length > 2 && strategicWinner && names.includes(strategicWinner)) {
      // More than 2 left: eliminate anyone except strategic winner
      const eliminationCandidates = names.filter(name => name !== strategicWinner);
      if (eliminationCandidates.length > 0) {
        const eliminationIndex = Math.floor(Math.random() * eliminationCandidates.length);
        const personToEliminate = eliminationCandidates[eliminationIndex];
        randomIndex = names.findIndex(name => name === personToEliminate);
      } else {
        // Fallback
        randomIndex = Math.floor(Math.random() * names.length);
      }
    } else {
      // Normal elimination (no strategic winner set or winner already eliminated)
      randomIndex = Math.floor(Math.random() * names.length);
    }
    
    const filterOutNames = names.filter((name) => name !== names[randomIndex]);
    setNames(filterOutNames);
    setInitialLoad(true);
  }

  function restartRaffle() {
    setInitialLoad(false);
    applyTimeFilter(timeFilter);  // Reset to current filtered list
    setWraffling(false);
    setShowConfetti(false);
    setStrategicWinner(null);  // Reset strategic winner for next raffle
  }

  useEffect(() => {
    if (initialLoad) {
      const filteringTimer = setTimeout(() => {
        startRaffle();
      }, 700);
      return () => {
        clearTimeout(filteringTimer);
      };
    }
  }, [initialLoad, names, startRaffle]);

  useEffect(() => {
    setWindowHeight(confettiWrapper.current.clientHeight);
    setWindowWidth(confettiWrapper.current.clientWidth);
  }, []);


  return (
    <div className="container" ref={confettiWrapper}>
      <div className="raffle-header">
        {/* Time Filter Section */}
        {!initialLoad && (
          <>
            <div className="time-filter-section">
              <h3>Select Participants:</h3>
              <div className="time-filter-buttons">
                <button 
                  className={`time-filter-btn ${timeFilter === 'all' ? 'active' : ''}`}
                  onClick={() => handleTimeFilterChange('all')}
                  disabled={loading}
                >
                  New Followers ({followerCounts['all']})
                </button>
              </div>
              <div className="fetch-controls">
                <button 
                  className="fetch-btn"
                  onClick={fetchFollowersData}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Reload New Followers'}
                </button>
                <button 
                  className="clear-fetch-btn"
                  onClick={clearAndFetchFresh}
                  disabled={loading}
                >
                  Clear & Get Fresh Data
                </button>
                <span className="participant-count">
                  {names.length} participants selected
                </span>
              </div>
            </div>

          <div className="raffle-header__buttons">
              <button 
                className="button-primary" 
                onClick={startRaffle}
                disabled={names.length === 0}
              >
                Start Raffle ({names.length} participants)
            </button>
            <button
              className="button-outline"
              onClick={() => setNames(shuffle(names))}
                disabled={names.length === 0}
            >
              Shuffle
            </button>
          </div>
          </>
        )}
      </div>
      {wraffling && (
        <Confetti
          recycle={showConfetti}
          numberOfPieces={80}
          width={windowWidth}
          height={windowHeight}
        />
      )}
      <div className="raffle-names">
        {transitions.map(({ item, props: { y, ...rest }, index }) => (
          <animated.div
            className="raffle-listnames"
            key={index}
            style={{
              transform: y.interpolate(y => `translate3d(0,${y}px,0)`),
              ...rest
            }}
          >
            <div className="raffle-namelist">
              <span>{item.name}</span> {/* Display full name */}
            </div>
          </animated.div>
        ))}
      </div>
      <div>
        {showConfetti && (
          <div className="raffle-ends">
            <h3>Congratulations! You have won the raffle!</h3>
            <button className="button-outline" onClick={restartRaffle}>
              Replay
            </button>
          </div>
        )}
      </div>
       {/* Bottom bar for logo */}
       <div className="bottom-bar">
        <img src={Logo} alt="Logo" className="bottom-bar-logo" />
      </div>
    </div>
  );
}

export default App;
