"""
Sample synthetic conversations for mental health knowledge graph applications.

IMPORTANT: These are entirely fictional conversations created for testing purposes.
They do not represent real individuals or clinical cases.

These simulate different types of mental health-related conversations:
- Clinical intake assessments
- Therapy session notes
- Care coordination discussions
- Support network conversations
- Treatment planning meetings

The knowledge graph can extract:
- Symptoms and their temporal patterns
- Treatment approaches and medications
- Care providers and their roles
- Support systems and relationships
- Triggers and coping strategies
"""

CONVERSATIONS = [
    # =========================================
    # CONVERSATION 1: Clinical Intake Assessment
    # =========================================
    {
        "name": "intake_assessment_001",
        "source_description": "Clinical intake assessment notes",
        "content": """
Clinician (Dr. Sarah Chen): Thank you for coming in today. Can you tell me what brought you here?

Patient: I've been struggling with anxiety for about six months now. It started after I lost my job 
at Meridian Tech in March. My primary care doctor, Dr. James Wilson, suggested I see a specialist.

Dr. Chen: I see. How has the anxiety been affecting your daily life?

Patient: I have trouble sleeping - maybe 4-5 hours a night. I've been avoiding social situations. 
My partner, Michael, has noticed I'm more irritable. I used to enjoy hiking with my friend group 
but haven't gone in months.

Dr. Chen: Have you experienced anxiety before this episode?

Patient: Yes, I had a similar period during college, around 2015. I saw a counselor at the 
university wellness center - I think her name was Dr. Patricia Moore. That helped a lot. 
I also have a family history - my mother has been treated for generalized anxiety disorder.

Dr. Chen: What coping strategies have you tried recently?

Patient: I started using the Calm app for meditation. My sister, Emma, recommended it. 
I've also cut back on caffeine. Dr. Wilson prescribed a low dose of sertraline last month, 
but I'm not sure it's helping yet.

Dr. Chen: Sertraline can take 4-6 weeks to reach full effect. I'd like to also recommend 
cognitive behavioral therapy. I can refer you to Dr. Rachel Martinez - she specializes in 
anxiety disorders and has availability.
"""
    },
    
    # =========================================
    # CONVERSATION 2: Care Coordination Meeting
    # =========================================
    {
        "name": "care_coordination_002",
        "source_description": "Multidisciplinary team meeting notes",
        "content": """
Dr. Chen: Let's discuss the care plan for our patient. I've been seeing them weekly for the 
past month. The anxiety symptoms have improved, but I'm concerned about emerging depressive symptoms.

Dr. Martinez (CBT Therapist): I agree. In our sessions, they've mentioned increased hopelessness 
about finding work. We've been working on cognitive restructuring, but progress has slowed.

Nurse Practitioner (Alex Thompson): I noticed at the last medication check that they've lost 
8 pounds since starting treatment. Sleep is still around 5 hours. Should we adjust the sertraline?

Dr. Chen: I'm considering adding bupropion to address the depression and help with energy levels. 
What do you think?

Dr. Martinez: That could help. I'd also like to involve their support system more. They mentioned 
their partner, Michael, and sister Emma are both very supportive. Family therapy might be beneficial.

Social Worker (Maria Garcia): I can reach out to coordinate. They also mentioned financial stress 
from job loss. I can connect them with our career counseling partner, Workforce Solutions, and 
look into short-term disability benefits.

Dr. Chen: Good plan. Let's also check in with their primary care provider, Dr. Wilson, to make 
sure we're aligned. Schedule a follow-up team meeting in two weeks.
"""
    },
    
    # =========================================
    # CONVERSATION 3: Therapy Session Notes
    # =========================================
    {
        "name": "therapy_session_015",
        "source_description": "CBT therapy session notes",
        "content": """
Dr. Martinez: How has your week been since we last met?

Patient: Mixed. I had a job interview at Horizon Analytics on Tuesday, which was terrifying but 
I managed to get through it. But Wednesday was really hard - I couldn't get out of bed until noon.

Dr. Martinez: Let's talk about Tuesday first. What anxiety symptoms did you notice before the interview?

Patient: Racing heart, sweaty palms. I used the breathing technique you taught me - the 4-7-8 method. 
It helped a bit. I also called my friend David before - he's been through a lot of interviews lately 
and gave me some encouragement.

Dr. Martinez: That's great use of your coping strategies and support network. What about Wednesday?

Patient: I think the interview exhausted me emotionally. Michael tried to help - he suggested we go 
for a walk, but I just couldn't. I felt guilty about that, which made me feel worse.

Dr. Martinez: Let's examine that guilt. What thoughts were going through your mind?

Patient: That I'm a burden. That Michael deserves someone who isn't broken. The same thoughts I had 
during my college episode.

Dr. Martinez: I hear echoes of what you experienced in 2015. Remember, you recovered then with 
Dr. Moore's help. What's different this time?

Patient: I guess... I have more tools now. And more support. My mother understands what I'm going 
through because of her own experience with anxiety. She's been checking in daily.
"""
    },
    
    # =========================================
    # CONVERSATION 4: Support Group Discussion
    # =========================================
    {
        "name": "support_group_session",
        "source_description": "Anxiety support group facilitated discussion",
        "content": """
Facilitator (Linda Park, LCSW): Welcome everyone. Let's start by checking in. How is everyone doing 
this week?

Member 1 (anonymized - "Alex"): Better than last week. I finally told my supervisor at work about 
needing accommodations for my anxiety. HR was actually supportive.

Linda: That took courage, Alex. How did it feel?

Alex: Scary but relieving. My therapist, Dr. Kim, helped me practice the conversation beforehand.

Member 2 ("Jordan"): I'm struggling. My medication was changed from escitalopram to venlafaxine 
and the transition has been rough. Lots of dizziness.

Linda: Medication changes can be challenging. Are you in touch with your prescriber?

Jordan: Yes, Dr. Patel said to give it two more weeks. My partner has been really patient with me. 
Having support at home makes a huge difference.

Member 3 ("Sam"): I can relate. When I switched medications last year, my sister stayed with me 
for a week. Family support is everything.

Linda: Support systems are so important. Alex mentioned workplace support, Jordan mentioned partner 
support, Sam mentioned family. What other support systems have helped people here?

Alex: My dog, honestly. And the Anxiety and Depression Association of America online forums. 
Sometimes it helps to connect with people going through similar things.

Sam: I started seeing a nutritionist, Dr. Rebecca Torres, who specializes in the gut-brain connection. 
It's been interesting exploring how diet affects my mood.
"""
    },
    
    # =========================================
    # CONVERSATION 5: Treatment Planning
    # =========================================
    {
        "name": "treatment_planning_review",
        "source_description": "Quarterly treatment plan review",
        "content": """
Dr. Chen: Let's review your progress over the past three months. When you first came in, your 
PHQ-9 score was 18 and your GAD-7 was 16. Today, they're 8 and 9 respectively.

Patient: That feels about right. I'm definitely better than I was in March.

Dr. Chen: The combination of sertraline and bupropion seems to be working. Dr. Martinez reports 
good progress in CBT as well. How do you feel about continuing this approach?

Patient: I want to keep going. The therapy has been really helpful - I'm actually using the 
techniques outside of sessions now. Michael says he's noticed a difference too.

Dr. Chen: Excellent. What about the other supports we put in place?

Patient: The career counseling through Workforce Solutions led to two interviews. I'm waiting 
to hear back from Horizon Analytics. Maria Garcia also helped me get temporary assistance, 
which reduced a lot of financial stress.

Dr. Chen: I'm glad the wraparound support is helping. What areas still need work?

Patient: Sleep is still not great. And I have a trip coming up to visit my mother in Portland - 
traveling triggers my anxiety. My sister Emma is going with me, which helps.

Dr. Chen: Let's talk about strategies for the trip. Also, I'd like to try adding a sleep-focused 
intervention. Dr. Thompson mentioned melatonin might help. We could also explore CBT for insomnia 
with Dr. Martinez.

Patient: I'd like that. Oh, and I wanted to mention - I reached out to Dr. Moore, my old counselor 
from college. She's retired now, but she was happy to hear I'm getting help again.
"""
    },
]

# Simpler test dataset for quick testing
QUICK_TEST = {
    "name": "quick_test_clinical",
    "source_description": "Brief clinical note",
    "content": """
Dr. Chen: Patient presents with symptoms of generalized anxiety disorder. Reports sleep 
disturbance (4-5 hours/night) and social withdrawal over 6 months. Previous episode in 2015 
treated successfully with therapy by Dr. Moore.

Current medications: Sertraline 50mg daily, prescribed by Dr. Wilson (PCP).

Support system includes partner Michael and sister Emma. Patient uses Calm app for meditation.

Plan: Refer to Dr. Martinez for CBT. Consider adding bupropion if depressive symptoms persist.
Follow-up in 2 weeks.
"""
}

# Entity types this data helps extract:
ENTITY_TYPES = """
This sample data demonstrates extraction of:

PEOPLE:
- Patients (anonymized)
- Clinicians (psychiatrists, therapists, social workers)
- Primary care providers
- Support network (family, friends, partners)

SYMPTOMS:
- Anxiety symptoms (racing heart, sleep disturbance, avoidance)
- Depression symptoms (hopelessness, fatigue, weight changes)
- Temporal patterns (onset, duration, triggers)

TREATMENTS:
- Medications (sertraline, bupropion, escitalopram)
- Therapy approaches (CBT, family therapy)
- Complementary approaches (meditation apps, nutrition)

ORGANIZATIONS:
- Healthcare facilities
- Support services (career counseling, support groups)
- Employers (relevant to occupational triggers)

RELATIONSHIPS:
- Care provider relationships (who treats whom)
- Support network connections (who supports whom)
- Treatment relationships (what treats what)
- Temporal relationships (when symptoms started, duration of treatment)
"""
