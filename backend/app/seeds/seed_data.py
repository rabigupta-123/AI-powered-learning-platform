"""Seed data matching the assignment specification, real course catalog, and sample scenario.
Role: Full Stack Developer
Skills:
- Python (R=70, I=0.8)
- SQL (R=60, I=0.6)
- HTML (R=50, I=0.5)
- JavaScript (R=80, I=1.0)
- React (R=75, I=1.0)
- Node.js (R=70, I=0.9)
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import (
    Skill, CareerRole, RoleSkillRequirement, LearningResource,
    User, UserSkill, UserCareerGoal, BKTState, UserSettings,
    Recommendation, Certificate, AssessmentQuestion, LearningRoadmap, RoadmapItem
)
from ..core.security import hash_password
from ..core.certificate import generate_certificate_pdf
from ..formulas.proficiency import calculate_skill_proficiency

def seed_database(db: Session):
    # 1. Create Skills
    skills_data = [
        {"name": "Python", "category": "Backend"},
        {"name": "SQL", "category": "Database"},
        {"name": "HTML", "category": "Frontend"},
        {"name": "JavaScript", "category": "Frontend"},
        {"name": "React", "category": "Frontend Framework"},
        {"name": "Node.js", "category": "Backend Runtime"},
    ]

    skill_records = {}
    for s_item in skills_data:
        skill = db.query(Skill).filter_by(name=s_item["name"]).first()
        if not skill:
            skill = Skill(name=s_item["name"], category=s_item["category"])
            db.add(skill)
            db.flush()
        skill_records[s_item["name"]] = skill

    # 2. Create Career Role: Full Stack Developer
    role_title = "Full Stack Developer"
    role = db.query(CareerRole).filter_by(title=role_title).first()
    if not role:
        role = CareerRole(
            title=role_title,
            description="Designs, builds, and maintains full-stack web applications across frontend UI, backend APIs, and databases."
        )
        db.add(role)
        db.flush()

    # 3. Create Role Skill Requirements
    requirements = [
        {"skill": "Python", "R_s": 70.0, "I_s": 0.8},
        {"skill": "SQL", "R_s": 60.0, "I_s": 0.6},
        {"skill": "HTML", "R_s": 50.0, "I_s": 0.5},
        {"skill": "JavaScript", "R_s": 80.0, "I_s": 1.0},
        {"skill": "React", "R_s": 75.0, "I_s": 1.0},
        {"skill": "Node.js", "R_s": 70.0, "I_s": 0.9},
    ]

    for req in requirements:
        skill = skill_records[req["skill"]]
        existing_req = db.query(RoleSkillRequirement).filter_by(role_id=role.id, skill_id=skill.id).first()
        if not existing_req:
            r_entry = RoleSkillRequirement(
                role_id=role.id,
                skill_id=skill.id,
                R_s=req["R_s"],
                I_s=req["I_s"]
            )
            db.add(r_entry)

    # 4. Create Real Course Catalog (Minimum 3 real free resources per skill = 18 total)
    resources_data = [
        # Python (3 Real Resources)
        {
            "title": "freeCodeCamp Scientific Computing with Python",
            "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
            "skill": "Python",
            "provider": "freeCodeCamp",
            "difficulty": 1,
            "est_hours": 20.0,
            "tags": "python, backend, fundamentals, algorithms, data-structures"
        },
        {
            "title": "Official Python 3 Documentation Tutorial",
            "url": "https://docs.python.org/3/tutorial/",
            "skill": "Python",
            "provider": "Python Software Foundation",
            "difficulty": 2,
            "est_hours": 15.0,
            "tags": "python, backend, oop, language-reference, standard-library"
        },
        {
            "title": "Real Python: Python Basics & Practical Exercises",
            "url": "https://realpython.com/python-basics/",
            "skill": "Python",
            "provider": "Real Python",
            "difficulty": 1,
            "est_hours": 12.0,
            "tags": "python, backend, syntax, programming, idioms"
        },

        # SQL (3 Real Resources)
        {
            "title": "SQLBolt: Interactive Lessons & Query Exercises",
            "url": "https://sqlbolt.com/",
            "skill": "SQL",
            "provider": "SQLBolt",
            "difficulty": 1,
            "est_hours": 10.0,
            "tags": "sql, database, queries, joins, fundamentals"
        },
        {
            "title": "Mode Analytics SQL Tutorial for Advanced Data Analysis",
            "url": "https://mode.com/sql-tutorial/",
            "skill": "SQL",
            "provider": "Mode",
            "difficulty": 2,
            "est_hours": 15.0,
            "tags": "sql, database, analytics, aggregation, subqueries, window-functions"
        },
        {
            "title": "W3Schools SQL Tutorial, Database Architecture & Exercises",
            "url": "https://www.w3schools.com/sql/",
            "skill": "SQL",
            "provider": "W3Schools",
            "difficulty": 1,
            "est_hours": 8.0,
            "tags": "sql, database, crud, tables, syntax, indexing"
        },

        # HTML (3 Real Resources)
        {
            "title": "MDN Web Docs: Structuring the Web with HTML",
            "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
            "skill": "HTML",
            "provider": "MDN Web Docs",
            "difficulty": 1,
            "est_hours": 12.0,
            "tags": "html, frontend, semantics, accessibility, web-standards"
        },
        {
            "title": "freeCodeCamp Responsive Web Design Certification",
            "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
            "skill": "HTML",
            "provider": "freeCodeCamp",
            "difficulty": 1,
            "est_hours": 25.0,
            "tags": "html, frontend, responsive, layout, forms, accessibility"
        },
        {
            "title": "W3Schools HTML5 Comprehensive Guide & Reference",
            "url": "https://www.w3schools.com/html/",
            "skill": "HTML",
            "provider": "W3Schools",
            "difficulty": 1,
            "est_hours": 8.0,
            "tags": "html, frontend, tags, web, elements, multimedia"
        },

        # JavaScript (3 Real Resources)
        {
            "title": "freeCodeCamp JavaScript Algorithms & Data Structures",
            "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
            "skill": "JavaScript",
            "provider": "freeCodeCamp",
            "difficulty": 1,
            "est_hours": 30.0,
            "tags": "javascript, frontend, algorithms, es6, fundamentals"
        },
        {
            "title": "MDN JavaScript Guide: Intermediate & Asynchronous Web APIs",
            "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "skill": "JavaScript",
            "provider": "MDN Web Docs",
            "difficulty": 2,
            "est_hours": 20.0,
            "tags": "javascript, frontend, async, dom, promises, closures"
        },
        {
            "title": "The Odin Project: Full Stack JavaScript Curriculum",
            "url": "https://www.theodinproject.com/paths/full-stack-javascript",
            "skill": "JavaScript",
            "provider": "The Odin Project",
            "difficulty": 2,
            "est_hours": 40.0,
            "tags": "javascript, frontend, web, project-based, dom, npm"
        },

        # React (3 Real Resources)
        {
            "title": "Official React Documentation: Learn React (Components & State)",
            "url": "https://react.dev/learn",
            "skill": "React",
            "provider": "React Core Team",
            "difficulty": 1,
            "est_hours": 25.0,
            "tags": "react, frontend, components, state, hooks, fundamentals"
        },
        {
            "title": "freeCodeCamp Front End Development Libraries (React & Redux)",
            "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/",
            "skill": "React",
            "provider": "freeCodeCamp",
            "difficulty": 2,
            "est_hours": 30.0,
            "tags": "react, frontend, redux, libraries, components, state-management"
        },
        {
            "title": "The Odin Project: Complete React Course & Routing",
            "url": "https://www.theodinproject.com/lessons/node-path-react-new-getting-started-with-react",
            "skill": "React",
            "provider": "The Odin Project",
            "difficulty": 2,
            "est_hours": 25.0,
            "tags": "react, frontend, hooks, routing, web, component-lifecycle"
        },

        # Node.js (3 Real Resources)
        {
            "title": "Official Node.js Guides: Architecture & Core Modules",
            "url": "https://nodejs.org/en/learn",
            "skill": "Node.js",
            "provider": "Node.js Foundation",
            "difficulty": 1,
            "est_hours": 20.0,
            "tags": "nodejs, backend, runtime, modules, asynchronous, event-loop"
        },
        {
            "title": "freeCodeCamp Back End Development & REST APIs with Express",
            "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
            "skill": "Node.js",
            "provider": "freeCodeCamp",
            "difficulty": 2,
            "est_hours": 35.0,
            "tags": "nodejs, express, backend, rest, api, mongodb, middleware"
        },
        {
            "title": "The Odin Project: Node.js, Express & Database Integration",
            "url": "https://www.theodinproject.com/paths/full-stack-javascript/courses/nodejs",
            "skill": "Node.js",
            "provider": "The Odin Project",
            "difficulty": 2,
            "est_hours": 30.0,
            "tags": "nodejs, backend, express, relational-db, authentication, security"
        },
    ]

    resource_records = {}
    for r_item in resources_data:
        skill = skill_records[r_item["skill"]]
        existing_res = db.query(LearningResource).filter_by(title=r_item["title"]).first()
        if not existing_res:
            existing_res = LearningResource(
                title=r_item["title"],
                url=r_item["url"],
                provider=r_item["provider"],
                skill_id=skill.id,
                difficulty=r_item["difficulty"],
                est_hours=r_item["est_hours"],
                tags=r_item["tags"]
            )
            db.add(existing_res)
            db.flush()
        resource_records[r_item["title"]] = existing_res

    # 5. Create Sample Learner Profile matching sample case
    demo_email = "demo@example.com"
    demo_user = db.query(User).filter_by(email=demo_email).first()
    if not demo_user:
        demo_user = User(
            name="Demo Learner",
            email=demo_email,
            password_hash=hash_password("DemoPass123!")
        )
        db.add(demo_user)
        db.flush()

        # Set user goal to Full Stack Developer
        user_goal = UserCareerGoal(
            user_id=demo_user.id,
            role_id=role.id,
            active=True
        )
        db.add(user_goal)

        # Set default user settings
        demo_settings = UserSettings(
            user_id=demo_user.id,
            theme="dark",
            llm_provider="gemini",
            llm_model="gemini-1.5-flash",
            llm_api_key_encrypted=None
        )
        db.add(demo_settings)

        # Populate user skills matching sample scenario
        sample_skills_init = {
            "Python": (80.0, 70.0, 60.0),
            "SQL": (60.0, 60.0, 60.0),
            "HTML": (50.0, 50.0, 50.0),
            "JavaScript": (0.0, 0.0, 0.0),
            "React": (0.0, 0.0, 0.0),
            "Node.js": (0.0, 0.0, 0.0),
        }

        for skill_name, (a_s, q_s, e_s) in sample_skills_init.items():
            skill = skill_records[skill_name]
            p_s = calculate_skill_proficiency(a_s, q_s, e_s)
            u_skill = UserSkill(
                user_id=demo_user.id,
                skill_id=skill.id,
                A_s=a_s,
                Q_s=q_s,
                E_s=e_s,
                P_s=p_s
            )
            db.add(u_skill)

            # Initialize BKT state (Python has 0.85 mastery for initial certificate!)
            p_mastery = 0.85 if skill_name == "Python" else (0.30 if p_s == 0.0 else round(min(0.75, p_s / 100.0), 2))
            bkt = BKTState(
                user_id=demo_user.id,
                skill_id=skill.id,
                p_mastery=p_mastery,
                p_T=0.15,
                p_G=0.20,
                p_S=0.10,
                attempts_count=2 if skill_name == "Python" else (1 if p_s > 0 else 0)
            )
            db.add(bkt)

        # Seed initial Recommendations immediately so Recommendations is never empty
        initial_recs = [
            ("freeCodeCamp JavaScript Algorithms & Data Structures", "JavaScript", 4.00),
            ("Official React Documentation: Learn React (Components & State)", "React", 3.00),
            ("Official Node.js Guides: Architecture & Core Modules", "Node.js", 2.10),
            ("MDN JavaScript Guide: Intermediate & Asynchronous Web APIs", "JavaScript", 2.667),
            ("freeCodeCamp Front End Development Libraries (React & Redux)", "React", 2.50),
            ("freeCodeCamp Back End Development & REST APIs with Express", "Node.js", 1.80),
        ]
        for title, s_name, prio in initial_recs:
            if title in resource_records:
                r_obj = resource_records[title]
                rec = Recommendation(
                    user_id=demo_user.id,
                    skill_id=r_obj.skill_id,
                    resource_id=r_obj.id,
                    priority_score=prio,
                    status="active"
                )
                db.add(rec)

        # Seed initial Certificate for Python (P(Ln) = 0.85 >= 0.80) so Certificates view has rows
        py_skill = skill_records["Python"]
        code, pdf_path = generate_certificate_pdf(
            learner_name=demo_user.name,
            skill_name="Python",
            role_title="Full Stack Developer",
            issued_at=datetime.now(timezone.utc)
        )
        cert = Certificate(
            user_id=demo_user.id,
            skill_id=py_skill.id,
            issued_at=datetime.now(timezone.utc),
            verification_code=code,
            pdf_path=pdf_path
        )
        db.add(cert)

    # 6. Additional Career Roles for multi-role career matching
    additional_roles = [
        {
            "title": "Frontend Engineer",
            "description": "Specializes in building responsive, accessible, high-performance web user interfaces.",
            "requirements": [
                {"skill": "HTML", "R_s": 80.0, "I_s": 0.8},
                {"skill": "JavaScript", "R_s": 90.0, "I_s": 1.0},
                {"skill": "React", "R_s": 85.0, "I_s": 1.0},
            ]
        },
        {
            "title": "Backend Engineer",
            "description": "Architects scalable APIs, database models, microservices, and high-throughput servers.",
            "requirements": [
                {"skill": "Python", "R_s": 85.0, "I_s": 1.0},
                {"skill": "SQL", "R_s": 80.0, "I_s": 0.9},
                {"skill": "Node.js", "R_s": 75.0, "I_s": 0.8},
            ]
        },
        {
            "title": "Data & AI Engineer",
            "description": "Develops data processing pipelines, SQL warehouses, and operationalizes machine learning models.",
            "requirements": [
                {"skill": "Python", "R_s": 90.0, "I_s": 1.0},
                {"skill": "SQL", "R_s": 85.0, "I_s": 0.9},
            ]
        }
    ]

    for r_spec in additional_roles:
        r_obj = db.query(CareerRole).filter_by(title=r_spec["title"]).first()
        if not r_obj:
            r_obj = CareerRole(title=r_spec["title"], description=r_spec["description"])
            db.add(r_obj)
            db.flush()
        for req in r_spec["requirements"]:
            if req["skill"] in skill_records:
                sk = skill_records[req["skill"]]
                existing_req = db.query(RoleSkillRequirement).filter_by(role_id=r_obj.id, skill_id=sk.id).first()
                if not existing_req:
                    db.add(RoleSkillRequirement(
                        role_id=r_obj.id,
                        skill_id=sk.id,
                        R_s=req["R_s"],
                        I_s=req["I_s"]
                    ))

    # 7. Seed Real Assessment Questions (4 per skill = 24 questions)
    if db.query(AssessmentQuestion).count() == 0:
        questions_data = [
            # Python
            {
                "skill": "Python",
                "question": "What is the primary difference between a list and a tuple in Python?",
                "a": "Lists are mutable while tuples are immutable",
                "b": "Lists only store integers; tuples store any type",
                "c": "Tuples cannot be indexed or sliced",
                "d": "Lists are immutable; tuples are dynamically sized",
                "correct": "A",
                "difficulty": 1,
                "explanation": "In Python, lists are mutable (can be changed after creation), whereas tuples are immutable sequence structures."
            },
            {
                "skill": "Python",
                "question": "Which Python keyword is used to yield values one by one in a generator function?",
                "a": "return",
                "b": "yield",
                "c": "async",
                "d": "generate",
                "correct": "B",
                "difficulty": 1,
                "explanation": "The 'yield' statement suspends function execution and returns a generator iterator value to the caller."
            },
            {
                "skill": "Python",
                "question": "What is the primary purpose of @functools.wraps when creating custom decorators?",
                "a": "Compiles the function into native C bytecode",
                "b": "Preserves the wrapped function's original metadata (__name__, __doc__)",
                "c": "Forces the function to execute asynchronously",
                "d": "Automatically adds exception retry handling",
                "correct": "B",
                "difficulty": 2,
                "explanation": "@functools.wraps copies name, docstring, and annotations from the original function to the decorator wrapper."
            },
            {
                "skill": "Python",
                "question": "What is the average time complexity of searching for a key in a Python dict?",
                "a": "O(n)",
                "b": "O(log n)",
                "c": "O(1)",
                "d": "O(n log n)",
                "correct": "C",
                "difficulty": 2,
                "explanation": "Python dictionaries use open-addressing hash tables, yielding average O(1) constant time lookup."
            },

            # SQL
            {
                "skill": "SQL",
                "question": "Which SQL JOIN returns all rows from the left table and matching rows from the right table?",
                "a": "INNER JOIN",
                "b": "LEFT JOIN",
                "c": "CROSS JOIN",
                "d": "RIGHT JOIN",
                "correct": "B",
                "difficulty": 1,
                "explanation": "A LEFT JOIN preserves every row from the left table, populating NULL for non-matching right table columns."
            },
            {
                "skill": "SQL",
                "question": "What is the fundamental difference between WHERE and HAVING in SQL?",
                "a": "WHERE filters rows before aggregation; HAVING filters groups after aggregation",
                "b": "WHERE applies only to text columns; HAVING applies only to numbers",
                "c": "HAVING can only be used with subqueries",
                "d": "There is no difference in modern relational databases",
                "correct": "A",
                "difficulty": 2,
                "explanation": "WHERE filters individual rows prior to GROUP BY aggregation; HAVING filters aggregated groups."
            },
            {
                "skill": "SQL",
                "question": "In relational database ACID properties, what does 'Atomicity' guarantee?",
                "a": "All transactions run at the speed of light",
                "b": "Either all operations in a transaction succeed, or none are applied (all-or-nothing)",
                "c": "Data is stored on atomic hardware partitions",
                "d": "Only one user can read the database at a time",
                "correct": "B",
                "difficulty": 2,
                "explanation": "Atomicity guarantees that multi-step transactions execute as a single atomic unit of work."
            },
            {
                "skill": "SQL",
                "question": "Which index structure is the standard default for B-Tree indexing in PostgreSQL and SQLite?",
                "a": "B-Tree index",
                "b": "Hash index",
                "c": "Inverted index",
                "d": "Bloom filter",
                "correct": "A",
                "difficulty": 1,
                "explanation": "B-Trees balance search, insertion, deletion, and range scans in O(log n) time."
            },

            # HTML
            {
                "skill": "HTML",
                "question": "Which semantic HTML5 tag should enclose the dominant unique content of a webpage?",
                "a": "<section>",
                "b": "<article>",
                "c": "<main>",
                "d": "<div>",
                "correct": "C",
                "difficulty": 1,
                "explanation": "The <main> tag designates the primary central content of the document body, excluding repeated headers/sidebars."
            },
            {
                "skill": "HTML",
                "question": "What is the accessibility purpose of the 'aria-label' attribute?",
                "a": "Styles elements with high contrast colors",
                "b": "Provides an explicit invisible text description for assistive technologies / screen readers",
                "c": "Automatically focuses the element on page load",
                "d": "Prevents right-clicking on sensitive elements",
                "correct": "B",
                "difficulty": 1,
                "explanation": "aria-label defines an accessible string label for assistive devices when visual text is absent or ambiguous."
            },
            {
                "skill": "HTML",
                "question": "What is the effect of placing the 'defer' attribute on a <script> tag?",
                "a": "Script is downloaded asynchronously and executed only after HTML parsing completes",
                "b": "Script download is blocked until user interacts with the page",
                "c": "Script runs immediately and stops HTML rendering",
                "d": "Script runs in a background Web Worker process",
                "correct": "A",
                "difficulty": 2,
                "explanation": "defer downloads external scripts in parallel without blocking parsing, executing them in document order after parsing."
            },
            {
                "skill": "HTML",
                "question": "Which meta viewport declaration ensures responsive scaling on mobile devices?",
                "a": "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
                "b": "<meta name='viewport' content='mobile-first=true'>",
                "c": "<meta name='viewport' content='width=1024, user-scalable=no'>",
                "d": "<meta name='responsive' content='true'>",
                "correct": "A",
                "difficulty": 1,
                "explanation": "width=device-width with initial-scale=1.0 matches the viewport to the device's screen pixels."
            },

            # JavaScript
            {
                "skill": "JavaScript",
                "question": "What is a closure in JavaScript?",
                "a": "A function that has access to variables from its outer (lexical) scope even after outer execution ends",
                "b": "A method that terminates a WebSocket or worker thread",
                "c": "A strict mode syntax for sealing object properties",
                "d": "An async function that returns a Promise",
                "correct": "A",
                "difficulty": 2,
                "explanation": "Closures allow an inner function to retain lexical bindings to its enclosing parent scope."
            },
            {
                "skill": "JavaScript",
                "question": "In the JavaScript Event Loop, which queue is drained immediately after the synchronous call stack?",
                "a": "Macrotask queue (setTimeout, setInterval)",
                "b": "Microtask queue (Promise.then, queueMicrotask)",
                "c": "I/O polling queue",
                "d": "requestIdleCallback queue",
                "correct": "B",
                "difficulty": 2,
                "explanation": "Microtasks have higher priority than macrotasks and are completely emptied at the end of each tick."
            },
            {
                "skill": "JavaScript",
                "question": "What is the result of evaluating `typeof null` in standard JavaScript?",
                "a": "'null'",
                "b": "'undefined'",
                "c": "'object'",
                "d": "'boolean'",
                "correct": "C",
                "difficulty": 1,
                "explanation": "In JavaScript, `typeof null` returns 'object', an infamous historic bug dating back to the first JS engine in 1995."
            },
            {
                "skill": "JavaScript",
                "question": "Which array method returns a single accumulated value from iterating over all elements?",
                "a": "map()",
                "b": "filter()",
                "c": "reduce()",
                "d": "find()",
                "correct": "C",
                "difficulty": 1,
                "explanation": "Array.prototype.reduce() runs a reducer callback across every element, accumulating into a single output."
            },

            # React
            {
                "skill": "React",
                "question": "What is the primary purpose of the dependency array in React's useEffect hook?",
                "a": "To register npm package dependencies at build time",
                "b": "To specify variables that trigger the effect callback when their values change",
                "c": "To define props passed from children to parent components",
                "d": "To force a component to re-mount every millisecond",
                "correct": "B",
                "difficulty": 1,
                "explanation": "React compares dependency array values via Object.is between renders, only re-running the effect when changed."
            },
            {
                "skill": "React",
                "question": "Why does React require unique 'key' props when rendering dynamic list elements?",
                "a": "To generate unique CSS class selectors for styling",
                "b": "To allow the Reconciliation algorithm to identify which items were modified, added, or removed efficiently",
                "c": "To prevent browser cross-site scripting vulnerabilities",
                "d": "To auto-sort list elements in alphabetical order",
                "correct": "B",
                "difficulty": 1,
                "explanation": "Keys provide identity to virtual DOM nodes, allowing diffing without needlessly destroying and re-creating DOM nodes."
            },
            {
                "skill": "React",
                "question": "Which hook should be used to memoize expensive computations between renders?",
                "a": "useCallback",
                "b": "useMemo",
                "c": "useRef",
                "d": "useContext",
                "correct": "B",
                "difficulty": 2,
                "explanation": "useMemo caches calculated values across renders until its specified dependencies update."
            },
            {
                "skill": "React",
                "question": "What is the core distinction between Props and State in React?",
                "a": "Props are external and read-only to the component; State is managed internally and can change over time",
                "b": "Props can only be numbers; State can only be strings",
                "c": "State is passed down to child components; Props are never shared",
                "d": "There is no difference in modern React 18",
                "correct": "A",
                "difficulty": 1,
                "explanation": "Props configure a component from its parent (immutable), whereas state stores local mutable component state."
            },

            # Node.js
            {
                "skill": "Node.js",
                "question": "Which multi-platform C library powers the event loop, thread pool, and async I/O in Node.js?",
                "a": "libuv",
                "b": "glibc",
                "c": "V8 engine",
                "d": "OpenSSL",
                "correct": "A",
                "difficulty": 2,
                "explanation": "libuv is the high-performance C library that implements Node's event loop, timers, and worker thread pool."
            },
            {
                "skill": "Node.js",
                "question": "In Express.js middleware, what happens if neither next() is called nor a response is sent?",
                "a": "Express automatically returns a 404 response",
                "b": "The client request hangs indefinitely until reaching the connection timeout",
                "c": "The Node.js server crashes with unhandled exception",
                "d": "The request is passed to the next route automatically",
                "correct": "B",
                "difficulty": 1,
                "explanation": "Without calling next() or sending res.send()/res.json(), the event loop leaves the socket connection open."
            },
            {
                "skill": "Node.js",
                "question": "Which Node.js core module provides utilities for working with file and directory paths across operating systems?",
                "a": "fs",
                "b": "path",
                "c": "os",
                "d": "url",
                "correct": "B",
                "difficulty": 1,
                "explanation": "The 'path' module handles Windows vs POSIX path delimiters and normalization seamlessly."
            },
            {
                "skill": "Node.js",
                "question": "What is the primary advantage of Node.js Streams when processing multi-gigabyte files?",
                "a": "Streams encrypt files with AES-256 automatically",
                "b": "Streams process data sequentially in small chunks, consuming minimal memory regardless of file size",
                "c": "Streams run completely synchronously on the main thread",
                "d": "Streams convert binary files into JSON arrays",
                "correct": "B",
                "difficulty": 2,
                "explanation": "Streams avoid buffering entire large files into RAM, piping data in manageable buffers."
            }
        ]

        for q in questions_data:
            if q["skill"] in skill_records:
                sk = skill_records[q["skill"]]
                db.add(AssessmentQuestion(
                    skill_id=sk.id,
                    question_text=q["question"],
                    option_a=q["a"],
                    option_b=q["b"],
                    option_c=q["c"],
                    option_d=q["d"],
                    correct_option=q["correct"],
                    difficulty=q["difficulty"],
                    explanation=q["explanation"]
                ))

    # 8. Seed Initial Adaptive Learning Roadmap for Demo Learner
    demo_user = db.query(User).filter_by(email="demo@example.com").first()
    fs_role = db.query(CareerRole).filter_by(title="Full Stack Developer").first()
    if demo_user and fs_role:
        existing_roadmap = db.query(LearningRoadmap).filter_by(user_id=demo_user.id, role_id=fs_role.id).first()
        if not existing_roadmap:
            roadmap = LearningRoadmap(
                user_id=demo_user.id,
                role_id=fs_role.id,
                title="Full Stack Developer Adaptive Pathway",
                is_active=True
            )
            db.add(roadmap)
            db.flush()

            stages = [
                {
                    "stage_order": 1,
                    "stage_title": "Stage 1: JavaScript & Asynchronous Foundations",
                    "skill": "JavaScript",
                    "difficulty": 1,
                    "est_hours": 20.0,
                    "status": "in_progress",
                    "prerequisites": "HTML, Python Basics"
                },
                {
                    "stage_order": 2,
                    "stage_title": "Stage 2: Frontend Engineering with React & Hooks",
                    "skill": "React",
                    "difficulty": 2,
                    "est_hours": 25.0,
                    "status": "not_started",
                    "prerequisites": "Stage 1: JavaScript Foundations"
                },
                {
                    "stage_order": 3,
                    "stage_title": "Stage 3: Scalable Backend Services with Node.js & Express",
                    "skill": "Node.js",
                    "difficulty": 2,
                    "est_hours": 20.0,
                    "status": "not_started",
                    "prerequisites": "Stage 1: JavaScript Foundations, SQL"
                },
                {
                    "stage_order": 4,
                    "stage_title": "Stage 4: Full Stack Architecture & REST API Integration",
                    "skill": "React",
                    "difficulty": 3,
                    "est_hours": 15.0,
                    "status": "not_started",
                    "prerequisites": "Stage 2 & Stage 3 Completion"
                }
            ]

            for stg in stages:
                sk = skill_records.get(stg["skill"])
                if sk:
                    db.add(RoadmapItem(
                        roadmap_id=roadmap.id,
                        skill_id=sk.id,
                        stage_order=stg["stage_order"],
                        stage_title=stg["stage_title"],
                        difficulty=stg["difficulty"],
                        est_hours=stg["est_hours"],
                        status=stg["status"],
                        prerequisites=stg["prerequisites"]
                    ))

    db.commit()
