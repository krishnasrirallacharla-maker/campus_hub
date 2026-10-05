/**
 * CampusHub - Initial Mock Database
 * Automatically seeds localStorage if no data exists.
 */

const INITIAL_DATA = {
  users: [
    {
      id: "usr_student_01",
      name: "Alex Johnson",
      email: "student@college.edu",
      password: "password123",
      role: "student",
      department: "Computer Science & Engineering",
      rollNo: "CS2024-089",
      semester: "6th Semester",
      phone: "+1 (555) 234-5678",
      bio: "Passionate about full-stack web development, AI hackathons, and open source software.",
      avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80"
    },
    {
      id: "usr_admin_01",
      name: "Dr. Sarah Jenkins",
      email: "admin@college.edu",
      password: "admin123",
      role: "admin",
      department: "Student Affairs & Event Committee",
      rollNo: "FAC-902",
      semester: "Faculty Head",
      phone: "+1 (555) 987-6543",
      bio: "Dean of Student Activities and Campus Event Coordinator.",
      avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80"
    }
  ],

  events: [
    {
      id: "evt_01",
      title: "HackSphere 2026: 36-Hour National Hackathon",
      category: "Tech",
      description: "Join over 500+ student developers, designers, and innovators for a thrilling 36-hour hackathon. Build innovative software and hardware prototypes with mentorship from top tech companies.",
      fullDescription: "HackSphere 2026 brings together the brightest minds across universities to solve pressing global challenges in AI, Web3, FinTech, and GreenTech. Compete for $10,000+ in prizes, network with industry sponsors, enjoy free food, swag, and nonstop coding workshops.",
      date: "2026-10-15",
      time: "09:00 AM - 09:00 PM",
      venue: "Main Campus Auditorium & Tech Labs",
      capacity: 300,
      registeredCount: 248,
      price: 0,
      status: "Published",
      image: "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
      organizer: "Computer Science Society & ACM Chapter",
      schedule: [
        { time: "09:00 AM", title: "Registration & Breakfast", desc: "Badge pick-up and opening refreshments" },
        { time: "10:30 AM", title: "Keynote & Problem Statements", desc: "Revealing tracks and sponsor bounties" },
        { time: "11:30 AM", title: "Hacking Begins", desc: "36 hours of non-stop building" },
        { time: "04:00 PM", title: "Mentor Rounds", desc: "1-on-1 architecture reviews with experts" }
      ],
      speakers: [
        { name: "David Chen", title: "Principal AI Scientist, Google Cloud", avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80" },
        { name: "Elena Rostova", title: "Founder & CEO, DevNexus", avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=150&q=80" }
      ]
    },
    {
      id: "evt_02",
      title: "Pulse 2026: Annual Inter-College Cultural Fest",
      category: "Cultural",
      description: "The grandest 3-day annual celebration of music, dance, theater, art exhibitions, and celebrity concert performances.",
      fullDescription: "Pulse is our university's flagship cultural extravaganza! Featuring battle of the bands, classical and contemporary dance battles, street theater, fashion shows, and a massive EDM night finale.",
      date: "2026-10-22",
      time: "10:00 AM - 10:00 PM",
      venue: "Open Air Amphitheatre & Student Center",
      capacity: 1200,
      registeredCount: 840,
      price: 15,
      status: "Published",
      image: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
      organizer: "Student Cultural Council",
      schedule: [
        { time: "10:00 AM", title: "Inaugural Ceremony", desc: "Traditional lamp lighting and welcome dance" },
        { time: "01:00 PM", title: "Battle of the Bands", desc: "12 college bands competing live" },
        { time: "06:30 PM", title: "Celebrity Artist Night", desc: "Live music and EDM concert" }
      ],
      speakers: [
        { name: "Marcus Vance", title: "Grammy-Nominated Music Producer", avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80" }
      ]
    },
    {
      id: "evt_03",
      title: "Generative AI & Agentic Systems Workshop",
      category: "Workshop",
      description: "Hands-on, deep-dive workshop into building LLM applications, autonomous agents, RAG pipelines, and vector databases.",
      fullDescription: "Step into the cutting edge of AI. Learn to build multimodal AI tools, use LangChain and LlamaIndex, connect vector stores, and deploy intelligent agents on the cloud with real-world project portfolios.",
      date: "2026-10-18",
      time: "02:00 PM - 06:00 PM",
      venue: "Innovation Hub - Room 402",
      capacity: 60,
      registeredCount: 58,
      price: 0,
      status: "Published",
      image: "https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=800&q=80",
      organizer: "Data Science & AI Club",
      schedule: [
        { time: "02:00 PM", title: "LLM Fundamentals & Prompt Engineering", desc: "Theory and token mechanics" },
        { time: "03:30 PM", title: "Hands-on Agent Building", desc: "Coding tools and memory modules" },
        { time: "05:15 PM", title: "Deployment & Q&A", desc: "Hosting on cloud API endpoints" }
      ],
      speakers: [
        { name: "Dr. Maya Lin", title: "AI Research Lead, DeepNeural", avatar: "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=150&q=80" }
      ]
    },
    {
      id: "evt_04",
      title: "Inter-University Basketball Championship",
      category: "Sports",
      description: "Cheer for your college varsity team in the high-stakes annual basketball tournament featuring 16 universities.",
      fullDescription: "The annual sports showdown kicks off! Witness electrifying slam dunks, fast breaks, and championship games over 4 thrilling days.",
      date: "2026-11-05",
      time: "08:30 AM - 05:00 PM",
      venue: "University Indoor Sports Complex",
      capacity: 500,
      registeredCount: 310,
      price: 5,
      status: "Published",
      image: "https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=800&q=80",
      organizer: "Department of Physical Education & Athletics",
      schedule: [
        { time: "08:30 AM", title: "Opening Match: Campus Wolves vs Ravens", desc: "Round of 16 match" },
        { time: "02:00 PM", title: "Quarter Finals", desc: "Knockout games" },
        { time: "04:30 PM", title: "Day 1 Wrap-up", desc: "Score announcements" }
      ],
      speakers: [
        { name: "Coach Robert Taylor", title: "Former National League Coach", avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80" }
      ]
    },
    {
      id: "evt_05",
      title: "Campus Esports Arena: Valorant & FC 26 Showdown",
      category: "Gaming",
      description: "Compete in the annual campus gaming tournament with 5v5 tactical shooter brackets and 1v1 console battles.",
      fullDescription: "Battle for the championship trophy and cash prizes in our high-octane esports showdown. Live streaming on Twitch with student casters!",
      date: "2026-10-28",
      time: "01:00 PM - 08:00 PM",
      venue: "Student Activity Center Gaming Lounge",
      capacity: 120,
      registeredCount: 110,
      price: 0,
      status: "Published",
      image: "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
      organizer: "Campus Gaming Guild",
      schedule: [
        { time: "01:00 PM", title: "Group Stage Matches", desc: "Double elimination bracket" },
        { time: "05:00 PM", title: "Semi-Finals", desc: "Best of 3 series" },
        { time: "07:00 PM", title: "Grand Finals & Trophy Ceremony", desc: "Main stage showdown" }
      ],
      speakers: [
        { name: "Samir 'Nova' Khan", title: "Pro Esports Caster", avatar: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80" }
      ]
    },
    {
      id: "evt_06",
      title: "Future of Clean Energy & Green Tech Seminar",
      category: "Seminar",
      description: "Distinguished keynote seminar on renewable solar innovations, microgrids, and circular engineering solutions.",
      fullDescription: "Industry pioneers and environmental scientists convene to discuss renewable energy transitions, battery chemistry breakthroughs, and student climate ventures.",
      date: "2026-11-12",
      time: "11:00 AM - 02:30 PM",
      venue: "Science Hall - Lecture Room 101",
      capacity: 150,
      registeredCount: 95,
      price: 0,
      status: "Published",
      image: "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?auto=format&fit=crop&w=800&q=80",
      organizer: "School of Environmental Engineering",
      schedule: [
        { time: "11:00 AM", title: "Keynote: Solar & Battery Revolution", desc: "Latest research benchmarks" },
        { time: "12:30 PM", title: "Panel Discussion: Sustainable Campus", desc: "Student & Faculty dialogue" },
        { time: "01:45 PM", title: "Student Project Exhibition", desc: "Live prototype showcase" }
      ],
      speakers: [
        { name: "Dr. Ananya Sharma", title: "Director of CleanTech Innovations", avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80" }
      ]
    }
  ],

  registrations: [
    {
      id: "reg_01",
      eventId: "evt_01",
      userId: "usr_student_01",
      userName: "Alex Johnson",
      userEmail: "student@college.edu",
      eventTitle: "HackSphere 2026: 36-Hour National Hackathon",
      eventDate: "2026-10-15",
      eventVenue: "Main Campus Auditorium & Tech Labs",
      registeredAt: "2026-09-28T14:30:00Z",
      ticketCode: "CH-HACK-8921",
      status: "Confirmed",
      attended: false
    },
    {
      id: "reg_02",
      eventId: "evt_03",
      userId: "usr_student_01",
      userName: "Alex Johnson",
      userEmail: "student@college.edu",
      eventTitle: "Generative AI & Agentic Systems Workshop",
      eventDate: "2026-10-18",
      eventVenue: "Innovation Hub - Room 402",
      registeredAt: "2026-09-29T10:15:00Z",
      ticketCode: "CH-AI-4310",
      status: "Confirmed",
      attended: false
    }
  ]
};

/**
 * Initialize Local Storage with default mock data if not already present
 */
function initLocalStorage() {
  if (!localStorage.getItem('campushub_events')) {
    localStorage.setItem('campushub_events', JSON.stringify(INITIAL_DATA.events));
  }
  if (!localStorage.getItem('campushub_users')) {
    localStorage.setItem('campushub_users', JSON.stringify(INITIAL_DATA.users));
  }
  if (!localStorage.getItem('campushub_registrations')) {
    localStorage.setItem('campushub_registrations', JSON.stringify(INITIAL_DATA.registrations));
  }
}

// Auto-run on script load
initLocalStorage();
