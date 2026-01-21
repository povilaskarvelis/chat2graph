"""
Clinical interview transcripts for mental health knowledge graph applications.

Source: Dr. Todd Grande's educational demonstration videos.

IMPORTANT: These are real interview transcripts, but the "patients" are ACTORS
performing scripted scenarios for educational purposes. They are NOT real patients
with actual diagnoses. The diagnostic determinations reflect what WOULD apply
if the presented symptoms were from a real patient.

Conditions demonstrated:
- Generalized Anxiety Disorder (GAD)
- Attention-Deficit/Hyperactivity Disorder (ADHD)
- Wernicke's Aphasia

The conversations demonstrate:
- DSM-5 diagnostic criteria assessment techniques
- Differential diagnosis approaches
- Screening for comorbidities
- Functional impairment assessment
- Subthreshold vs. threshold presentations

Metadata fields:
- diagnosis: The condition being assessed in the demonstration
- meets_criteria: Whether the ACTOR'S portrayed symptoms meet DSM-5 criteria
"""

CONVERSATIONS = [
    # =========================================
    # CONVERSATION 1: GAD - Sarah (Meets Criteria)
    # =========================================
    {
        "name": "gad_sarah_001",
        "source_description": "Clinical intake - GAD assessment (meets criteria)",
        "diagnosis": "Generalized Anxiety Disorder",
        "meets_criteria": True,
        "content": """
Dr. Todd Grande: Hi Sarah, how you doing today?

Sarah: Um, I'm doing okay. Could be a little better, but I could always be worse. But I'm doing okay.

Dr. Todd Grande: Doing okay? I understand you have some symptoms that have been bothering you.

Sarah: Um... they have been bothering me. Well, I just started back to school last year. I... I was staying at home while my husband was working but the kids are growing now, out of the house. So I said I was going to go back to school. I haven't been in school in 20 years. And I thought I could handle it. But right now I just find myself so anxious and just so worried all the time. And I just don't know what to do with it. It's been going on for around the past seven, eight months now.

Dr. Todd Grande: About seven or eight months?

Sarah: Yeah.

Dr. Todd Grande: All right. Would you say that this um... anxiety has been affecting you more days than it doesn't?

Sarah: Um, I would say it's been affecting me yes. For some time now, yes. More often than not, yes.

Dr. Todd Grande: More often than not. Yeah. Do you find yourself struggling to control the anxiety?

Sarah: To control it? Um... I'm just anxious all the time. Yes.

Dr. Todd Grande: All right, so it sounds like you are struggling to take it under control.

Sarah: Yes.

Dr. Todd Grande: Tell me about how it's been affecting... you mentioned school?

Sarah: It's... I'm not doing too well in school right now. Not at all.

Dr. Todd Grande: In what way?

Sarah: I thought I would be a better student. I was always a straight-A student back... back before when I was in undergrad I was always a straight-A student. But now I'm failing and I... I just can't... I can't concentrate in school. I'm failing. I'm just so worried all the time about what... how I'm going to do in this class, what assignments are due, if I'm getting the work done in time. And it's just controlling... it's taking over everything I do in school. So I'm so more... I'm more worried about how I'm going to do than having time to focus on my grades. Like it's just to that level.

Dr. Todd Grande: That's really distressing for you.

Sarah: Yes.

Dr. Todd Grande: And that's at school. How about at home?

Sarah: At home I'm so worried about school that it's affecting my life at home. Like I'm... okay I have this assignment but then... oh my goodness I'm so focused on this assignment, will I have time to make dinner for the kids? Oh my husband's going... oh the house is such a mess all the time. And it's just causing so much conflict at home. My husband thinks I should be doing my housework and I'm so consumed with school and then it's just such a big mess right now. So I'm constantly worried. When I'm in... when I'm at school I'm worried about home, and when I'm home I'm worried about school.

Dr. Todd Grande: So a good deal... good deal of worrying all the time.

Sarah: Yes. All the time.

Dr. Todd Grande: Okay. So I want to ask you a few questions about this uh... and some that might be related. Do you um... drink or use any drugs?

Sarah: No, not at all.

Dr. Todd Grande: Not at all. Do you have any uh... medical conditions?

Sarah: No, not at all. Nothing.

Dr. Todd Grande: Have you ever been diagnosed with any other mental health disorders?

Sarah: No. None.

Dr. Todd Grande: Do you ever have uh... panic attacks?

Sarah: No.

Dr. Todd Grande: Have you ever had one in the past?

Sarah: Um, no. No.

Dr. Todd Grande: No. So a lot of anxiety but no panic? Just... just anxiety like overwhelming anxiety?

Sarah: Intense anxiety. Yes.

Dr. Todd Grande: But... but never a situation where you felt you had to flee from a room or anything like that?

Sarah: No. No.

Dr. Todd Grande: Any past trauma?

Sarah: No. Nothing like that.

Dr. Todd Grande: Okay. Do you sometimes feel keyed up, on edge, or restless?

Sarah: Um... restless, yes. Restless.

Dr. Todd Grande: Restless. All right. Do you find yourself easily fatigued?

Sarah: Um... tired all the time. Tired all the time. Yes.

Dr. Todd Grande: Do you have any trouble concentrating or finding your mind going blank?

Sarah: No, not really. No. Just no.

Dr. Todd Grande: How about um... irritability? You find yourself irritable?

Sarah: No. No. Not really irritable.

Dr. Todd Grande: Any muscle tension?

Sarah: No. Not really. No.

Dr. Todd Grande: Okay. How about any need... trouble sleeping? So this would be falling asleep, staying asleep, having unsatisfying sleep... anything like that?

Sarah: Well I have unsatisfying sleep, but we just moved and we live next to a factory. There's trucks in and out all the time. Who can sleep with that? Just chronic... just noise.

Dr. Todd Grande: So you think that might be causing your sleep disturbance?

Sarah: Um... it's entirely possible. It's like who can sleep when you got trucks in and out all hours of the night... overnight... and in the wee hours of the morning? So it's pretty much impossible to fall asleep when you have just this noise.

Dr. Todd Grande: How about before you moved there?

Sarah: Um... I don't remember.

Dr. Todd Grande: Don't remember?

Sarah: I really don't remember.

Dr. Todd Grande: How long ago was it that you moved there for now?

Sarah: Um... couple years.

Dr. Todd Grande: But a couple years?

Sarah: Yes.

Dr. Todd Grande: So you've had this noise at night for a couple years?

Sarah: Yes.

Dr. Todd Grande: And symptoms started eight months ago?

Sarah: Yes.

Dr. Todd Grande: All right. So I don't know if they've made it... I don't know if it made it... if it's made it worse or... but just the noise has just been so... I don't know if it's the noise or what but I can't sleep through a truck.

Dr. Todd Grande: Okay. How about um... any vacations or anything?

Sarah: I'm sorry. I'm sorry. No. No vacations.

Dr. Todd Grande: All right so you've pretty much been sleeping at your home every night for as long as the symptoms have been around?

Sarah: Oh yes. Yeah.

Dr. Todd Grande: All right. All right Sarah, um... I appreciate you answering these questions for me. This has been helpful. I'm going to get you scheduled with the counselor and they should be able see you in a couple days.

Sarah: Oh thank you. Thank... I would... I would so appreciate it just to get this under control.

Dr. Todd Grande: Absolutely. Take care Sarah.

Sarah: Thank you.
"""
    },

    # =========================================
    # CONVERSATION 2: ADHD - Elise (Does NOT Meet Criteria)
    # =========================================
    {
        "name": "adhd_elise_001",
        "source_description": "Clinical intake - ADHD assessment (does not meet criteria)",
        "diagnosis": "ADHD (self-suspected)",
        "meets_criteria": False,
        "content": """
Dr. Todd Grande: Hi Elise, how you doing today?

Elise: Um, doing pretty well. But uh... I'm kind of concerned about something.

Dr. Todd Grande: Yeah? I... I'm aware you have some symptoms that have been bothering you. Can you tell me about those?

Elise: Yeah, uh... sometimes I have problems like... with my attention. And you know, I was looking it up online, and I... I'm really worried that I might have ADHD.

Dr. Todd Grande: ADHD?

Elise: Yeah.

Dr. Todd Grande: All right. So we'll... we'll talk about that. Let me ask you a few quick questions before we... we get to that. Um, do you ever feel depressed?

Elise: No.

Dr. Todd Grande: No. Anxious?

Elise: No.

Dr. Todd Grande: Any trouble with drugs or alcohol? Anything like that?

Elise: Oh no. Nothing like that.

Dr. Todd Grande: Okay. Um, why do you think you have... have ADHD?

Elise: Oh, cause I mean I've always had a problem with my attention. Um, and I can get distracted very easily.

Dr. Todd Grande: All right, so... so trouble establishing attention?

Elise: Yes.

Dr. Todd Grande: How about difficulty in holding attention? Like once you have established it?

Elise: Yeah. Trouble with both of those.

Dr. Todd Grande: Trouble with both of those. All right. And you mentioned the word distracted?

Elise: Yes.

Dr. Todd Grande: So you find yourself easily distracted?

Elise: Yes I do.

Dr. Todd Grande: Okay. How about um... well give me an idea of the setting. So is this at work or school?

Elise: Oh, it's everywhere.

Dr. Todd Grande: It's everywhere?

Elise: It's everywhere.

Dr. Todd Grande: All right. So do you work?

Elise: Yes I do.

Dr. Todd Grande: Yeah. Do you go to school?

Elise: Yes I do.

Dr. Todd Grande: How old are you?

Elise: I'm 24.

Dr. Todd Grande: 24. All right. And this problem with the attention affects you at work?

Elise: Yeah.

Dr. Todd Grande: And at school?

Elise: Mhm.

Dr. Todd Grande: And you... you said everywhere.

Elise: Yeah. Pretty much just part of my everyday life now.

Dr. Todd Grande: All right. You're 24 now. When did you first notice the attention problems?

Elise: Oh I've always had that. Uh, I mean even when I was in like elementary school. You know, I was always that kid.

Dr. Todd Grande: You've had it for a long time.

Elise: Yeah. Yeah.

Dr. Todd Grande: How about uh... how disturbing is it? Like how much is it interfering with your functioning?

Elise: It really... it really does. It's really problematic.

Dr. Todd Grande: Wow. All right. Okay, so I'm going to ask you a few other questions here. We talked about the attention. So it's hard for you to give attention and hold attention.

Elise: Yeah.

Dr. Todd Grande: How about listening? Let's... let's go with the um... the school environment for now. Let's talk about uh... school. How about listening in class?

Elise: No, I don't really have a problem with that.

Dr. Todd Grande: That's not a problem for you?

Elise: No.

Dr. Todd Grande: How about following instructions?

Elise: No.

Dr. Todd Grande: Tell me about your organizational skills.

Elise: I'm very organized.

Dr. Todd Grande: You're very organized?

Elise: Yeah. Have to be in college.

Dr. Todd Grande: Do you find yourself avoiding um... activities that require a lot of mental investment? Mental energy?

Elise: No, not really. No.

Dr. Todd Grande: No. All right. Do you... do you move toward those type of activities?

Elise: Well I'm not opposed to them. Like I like chess and... checkers.

Dr. Todd Grande: All right. Do you ever find yourself losing things that you need to complete different jobs or tasks?

Elise: No. No.

Dr. Todd Grande: Okay. I'm going to change gears and ask you some other questions around a different area. Okay?

Elise: Okay.

Dr. Todd Grande: Do you ever find yourself like fidgeting? Tough to stay still?

Elise: Not really, no. No.

Dr. Todd Grande: In school... again we'll kind of stick with the... school environment. Okay? Uh, do you find it difficult to stay seated?

Elise: No, not at all. No.

Dr. Todd Grande: How do you do when you are engaging in a quiet activity?

Elise: Um, I do pretty well.

Dr. Todd Grande: You do okay with that?

Elise: Yeah.

Dr. Todd Grande: You don't find yourself wandering off?

Elise: No.

Dr. Todd Grande: With that? Okay. Do you ever feel like uh... like internally there's a motor running and you can't shut it off?

Elise: No. No.

Dr. Todd Grande: How about um... being talkative? Do you find yourself very talkative?

Elise: I'm very talkative. Very talkative. Sometimes I... I end up being rude and I interrupt people. I just... I got to get it out.

Dr. Todd Grande: All right, so you feel like you talk a lot and that you interrupt?

Elise: Yes I do. Interrupt people.

Dr. Todd Grande: In a situation where it would be traditional to like wait in line or wait your turn... do you find that's difficult for you?

Elise: No. No.

Dr. Todd Grande: Do you ever find yourself like for example in class just saying something... like blurting something out without giving it much thought?

Elise: No. Not really. No.

Dr. Todd Grande: Okay. All right. I think I have what I need here. Uh, and I want to get you in to see a counselor.

Elise: Okay.

Dr. Todd Grande: If that works for you. Cuz you did mention this was affecting your functioning.

Elise: Yes.

Dr. Todd Grande: Want to make sure you get to see a counselor. It'll just take a couple days to get you in to see somebody if that works for you.

Elise: That's great. Thank you.

Dr. Todd Grande: Yeah I appreciate you taking this time with me. This uh... information has been helpful.

Elise: Thank you very much.

Dr. Todd Grande: Thanks Elise.
"""
    },

    # =========================================
    # CONVERSATION 3: ADHD - Elise (Meets Criteria)
    # =========================================
    {
        "name": "adhd_elise_002",
        "source_description": "Clinical intake - ADHD assessment (meets criteria)",
        "diagnosis": "ADHD Combined Presentation",
        "meets_criteria": True,
        "content": """
Dr. Todd Grande: Hi Elise, how you doing today?

Elise: Well, I guess I'm doing okay, but... I'm having some problems.

Dr. Todd Grande: What's going on?

Elise: Ah, I found myself getting really distracted, kind of fidgety and stuff. And I think I might have that uh... that one disorder that I hear about all the time on TV, like ADHD?

Dr. Todd Grande: Yeah? That's the one you think you might have? ADHD?

Elise: Yeah.

Dr. Todd Grande: All right. So let me ask you some other questions and then we'll get into some questions specifically about that and see what's going on there. Okay? Do you ever find yourself depressed?

Elise: Yeah.

Dr. Todd Grande: Anxious?

Elise: Hey...

Dr. Todd Grande: Trouble with drugs or alcohol?

Elise: Oh yeah... nothing like that.

Dr. Todd Grande: Nothing like that. When did you first notice you had the symptoms?

Elise: Um, early teens? Maybe before.

Dr. Todd Grande: Do you know what age?

Elise: No. No.

Dr. Todd Grande: All right, but you think early teens, maybe before. Do the symptoms... are they really bothersome to you?

Elise: They cause me... yeah. Yeah.

Dr. Todd Grande: What kind of areas do they cause you problems?

Elise: Ah, I mean really all... everywhere I guess.

Dr. Todd Grande: Yeah? Do you work?

Elise: Yes, I do.

Dr. Todd Grande: Does this cause problems at work?

Elise: Yes.

Dr. Todd Grande: How about college?

Elise: Yes it does.

Dr. Todd Grande: Okay. How about at home?

Elise: Oh yeah. Big trouble.

Dr. Todd Grande: All right. So tell me a little bit about the symptoms that you think might indicate ADHD. What's going on?

Elise: Well I mean when I go to class and I find myself... you know, kind of going off into my little world where the teacher's talking. Um, it's kind of like I just... I can't stand sitting down. And then I'll stand up and the teacher's looking at me like "Do you need something?" even like... no. No, I just really needed to stand up.

Dr. Todd Grande: Nice. You feel compelled to... to stand up in class?

Elise: Yes.

Dr. Todd Grande: Even though you know it might draw some attention?

Elise: Yeah... people start looking. I know it but I still need to do it.

Dr. Todd Grande: All right. So I'm going to ask you a few questions... and yes, you got two categories of questions. Okay?

Elise: Right.

Dr. Todd Grande: So I'll start the first category. Do you feel like you have trouble establishing attention? Let's look at this... say in terms of school.

Elise: Yes.

Dr. Todd Grande: You do? Okay. How about when you have established attention? Do you find yourself struggling to hold on to it?

Elise: Yes. Yes.

Dr. Todd Grande: And again I'll just stick with the school environment, right? That's a place where these symptoms bother you?

Elise: Well at school, yeah. I can... they bother places... other places, but...

Dr. Todd Grande: It does? Listen, big issue. That's a big one. Okay, do you have trouble listening in class?

Elise: Yes, I do.

Dr. Todd Grande: How about um... following through on instructions that are provided by say the professor?

Elise: Yes. Yeah, class projects are the hardest.

Dr. Todd Grande: Do you find yourself organized?

Elise: Yeah, I am pretty organized.

Dr. Todd Grande: You're pretty organized. Do you find yourself in school or other settings avoiding activities that require a lot of mental effort?

Elise: Yes. Yeah. Yeah, they give me a headache and I just don't want to do with it.

Dr. Todd Grande: What are some things you avoid?

Elise: Oh, board games. I can't stand chess. I just don't understand it. And the people explain to me the rules and I just zone out.

Dr. Todd Grande: Ever find yourself losing things that you need to... to function at work or school?

Elise: No. No.

Dr. Todd Grande: Distracted?

Elise: Yes.

Dr. Todd Grande: When... do you get distracted fairly easily?

Elise: Yeah. Yeah.

Dr. Todd Grande: How about forgetfulness?

Elise: Yeah, I am pretty bad for that. For... okay.

Dr. Todd Grande: So I'm gonna move and ask you another category of questions. Okay?

Elise: Okay.

Dr. Todd Grande: Do you find yourself fidgeting?

Elise: Yes. Yeah.

Dr. Todd Grande: How do you do with... I think we touched on this before, but... how do you do with quiet activities? Like for example reading?

Elise: All right... I really struggle with that.

Dr. Todd Grande: You struggle with that?

Elise: Yeah. I can play video games for an hour but I can't read or play games or draw.

Dr. Todd Grande: So when you are engaged in quiet activities, do you find yourself kind of wandering off?

Elise: Yes. You do.

Dr. Todd Grande: All right. You ever feel like you have an internal motor that won't shut off?

Elise: No, I wouldn't say that. No.

Dr. Todd Grande: Okay. Do you feel like you talk excessively?

Elise: Yes. Yeah. Yeah, almost to the point that I... annoying, you know? I interrupt people a lot.

Dr. Todd Grande: What settings do you find that's a problem?

Elise: School's a big one.

Dr. Todd Grande: That's a big one?

Elise: Yeah. Because I'll talk and I'll talk. I mean I'll get off track when called on by the teacher and then somebody else will say something and be like "Oh yeah, I know, I forgot." Yeah that too. And I mean I feel horrible but I just... I can't stop it.

Dr. Todd Grande: You ever find that say in class you blurt things out?

Elise: Yes. Yeah.

Dr. Todd Grande: And interrupt people?

Elise: Yes, I do it wrong.

Dr. Todd Grande: You do that. Okay. How about a situation where... say work or school... or at home... where you have to wait your turn for something? Do you find that's a problem?

Elise: Well like at a drive through...

Dr. Todd Grande: Hey, it could be a drive through. If you're at a drive through, do you find... I mean, you don't have any trouble with like waiting in lines or waiting for your turn?

Elise: I guess not. It's not...

Dr. Todd Grande: Okay. Okay. All right so I'm gonna get you in to see one of our counselors. You mentioned that these symptoms are bothersome to you. I want to make sure you get treated. Take a couple days to get you in to see somebody. Is that okay?

Elise: Yes, that's fine. Please.

Dr. Todd Grande: I want to thank you for spending this time with me and answering these questions. This has been really helpful.

Elise: Thank you.

Dr. Todd Grande: Thanks Elise.
"""
    },

    # =========================================
    # CONVERSATION 4: ADHD - Elise (Online Student)
    # =========================================
    {
        "name": "adhd_elise_003",
        "source_description": "Clinical intake - ADHD assessment (online student, limited impairment domains)",
        "diagnosis": "ADHD Combined Presentation",
        "meets_criteria": True,
        "notes": "Patient attends online college, which may mask some impairment",
        "content": """
Dr. Todd Grande: Hi Elise, how you doing today?

Elise: Oh, guess I'm doing pretty good.

Dr. Todd Grande: Doing pretty good?

Elise: Well... so I was looking up online uh, during break... through my classes, I go to online school...

Dr. Todd Grande: Online college, yeah?

Elise: And they have this... I was looking at up my symptoms, I guess. Difficulty paying attention, difficulty staying still, just stuff like that. And you know, I think I might have that uh... that one disorder... ADHD?

Dr. Todd Grande: Yeah? That one... think you may have ADHD?

Elise: Yeah.

Dr. Todd Grande: All right. Is it... these symptoms bothering you? You said you go to college online?

Elise: Yes. Yeah, it does. It does.

Dr. Todd Grande: All right. I'm gonna ask you a few questions and try to get a better understand what's going on. Okay?

Elise: Okay.

Dr. Todd Grande: These symptoms you've been having... at what age did they start?

Elise: Years old.

Dr. Todd Grande: All right. And you feel like they're bothering you with your classes?

Elise: Did you take online? Yes... but I stopped. I still get good grades.

Dr. Todd Grande: You still get good grades?

Elise: Yeah.

Dr. Todd Grande: All right so I'm gonna ask you some questions about that. So I'll specifically be asking about how it affects you in... in class, but if affects you in any other area tell me about that too. Okay?

Elise: All right.

Dr. Todd Grande: Do you have trouble establishing attention?

Elise: Yes.

Dr. Todd Grande: When you have established attention, you have difficulty holding attention?

Elise: Yes.

Dr. Todd Grande: Do for example... with the professor... do you listen to the professor in your online classes?

Elise: Why?

Dr. Todd Grande: Difficulty listening? That's a problem for you?

Elise: How about following through on any instructions the professor gives you? Oh I have a problem, yeah.

Dr. Todd Grande: Are you organized?

Elise: [Silence/No response]

Dr. Todd Grande: Do you find yourself avoiding activities that require a lot of mental effort?

Elise: Yes. Yeah.

Dr. Todd Grande: What type of activities do you avoid?

Elise: Oh anything that's just like riddles. I can't stand them. Mm-hmm. Chess. Can't stand it. People try to explain to me the rules, I still don't get it. I get a headache and I quit.

Dr. Todd Grande: All right. Do you ever find yourself losing things that you need for class or any other place?

Elise: All the time. Yeah.

Dr. Todd Grande: Are you easily distracted?

Elise: Yes. Big time.

Dr. Todd Grande: Are you forgetful?

Elise: Yes. Yeah.

Dr. Todd Grande: So I'm gonna move to another series of questions. All right? Do you fidget?

Elise: Yes. You do? I do.

Dr. Todd Grande: Do you find it difficult to stay in your seat?

Elise: Yes. Stairs... we have these videos and sometimes I just... I gotta pause 'em and I just gotta walk around the room for a while. You know, go back, sit down... and on my system click "we're good."

Dr. Todd Grande: Okay. So you feel kind of compelled to stand up and walk around?

Elise: Yes.

Dr. Todd Grande: And then you can sit down and resume?

Elise: Yeah.

Dr. Todd Grande: How do you do with quiet activities like reading?

Elise: No. No, I don't... I don't like doing them because I just can't... I can't deal with the quiet. No. No.

Dr. Todd Grande: All right. You ever feel like you have an internal motor that's always running?

Elise: Yes. Yeah.

Dr. Todd Grande: How about talking? You find that you talk excessively?

Elise: Yes I do.

Dr. Todd Grande: How about blurting things out?

Elise: Yes, but people don't really notice it because especially at class I'll like yell out the answer but you have to hit a button...

Dr. Todd Grande: And hit a button? So that... okay. Turn these on and the audio transmits. All right, so you'll... you'll blurt something out but they won't hear it?

Elise: Yeah they won't. Because you have it so I guess that's good.

Dr. Todd Grande: Okay. Okay. How about interrupting people?

Elise: Yes. Yeah. Yes.

Dr. Todd Grande: Do you have trouble waiting your turn?

Elise: Back to the... the blurting out. I forget to hit the button. I then hit the button to answer and that goes something like this line... I hate waiting for my turn. I can't... I can't deal with it.

Dr. Todd Grande: Okay. No, that's not... not a strong suit for you.

Elise: No.

Dr. Todd Grande: Okay. So you mentioned that this is causing some difficulty in school, but you also said that you doing okay in school?

Elise: Yeah.

Dr. Todd Grande: All right. Is there any other area of your life where this is causing you problems?

Elise: Not that I can think of now. No.

Dr. Todd Grande: Yeah. What else do you do? So you go to college?

Elise: Yeah.

Dr. Todd Grande: What activities do you engage in?

Elise: Where's like... nothing. I got a full... course load. I'm trying to get it done. Really don't do anything else. I mean, ya know.

Dr. Todd Grande: How about like relatives?

Elise: I don't see my relatives a lot. Like my parents retired, they moved, so I don't see them. I don't see them.

Dr. Todd Grande: How about friends?

Elise: It's kind of embarrassing... if I really don't have any friends. Just kind of live, eat, breathe school.

Dr. Todd Grande: Do you ever socialize with any of your classmates from college?

Elise: No. No.

Dr. Todd Grande: Do you feel that's because of these symptoms? Or did... you wouldn't anyway?

Elise: Well I feel bad about it. So I mean it's hard for me to... you know, to get over it cause I notice it. But it's hard for me to get out there.

Dr. Todd Grande: All right. Do you think it's hard for you to engage with a classmate socially because of any concentration or hyperactivity type symptoms?

Elise: That's what I believe. Yeah.

Dr. Todd Grande: You believe it is cause those symptoms?

Elise: Yeah.

Dr. Todd Grande: And any other areas like... like shopping or cleaning the house? That works out okay?

Elise: Yeah.

Dr. Todd Grande: All right. Okay Elise, I'm gonna get you in to see a counselor. So just take a couple days to get you in. Right? So I set an appointment for a couple days out. I appreciate you spending this time with me and let me ask these questions. This was helpful.

Elise: Thank you.

Dr. Todd Grande: Thanks.
"""
    },

    # =========================================
    # CONVERSATION 5: GAD - Sarah (With Comorbidities)
    # =========================================
    {
        "name": "gad_sarah_002",
        "source_description": "Clinical intake - GAD with substance use and trauma history",
        "diagnosis": "Generalized Anxiety Disorder",
        "meets_criteria": True,
        "comorbidities": ["Alcohol use", "Cannabis use", "Possible trauma history"],
        "content": """
Dr. Todd Grande: Hi Sarah, how you doing today?

Sarah: Eh, I'm okay. Could be better, but could be worse. Um, I'm hanging in there.

Dr. Todd Grande: You're hanging in there?

Sarah: Yeah.

Dr. Todd Grande: I understand you've been having some symptoms that have been bothering you. Can you tell me about those?

Sarah: Oh, I'm worried all the time. And just every day, all day, just so worried about everything. I... I've just started back to school after 20 years. I, you know, I've been a housewife, the kids are now grown, so why not go back to school? And now for the past seven, eight months it's just been nothing but worry, worry, worry constantly all the time. Worried about home, worried about school, and it's affecting my life.

Dr. Todd Grande: All right, so... so a lot of... a lot of worrying. And how many... how many days would you say you worry in a typical week?

Sarah: Tuh... how many days don't I worry? Um, I'd say most days. Monday through Friday, Saturday, Sunday... it's just always worrying. When I'm... on Monday through Friday I'm worried about school, or when I'm at school I'm worried about home. And then on the weekends, I know the school week's coming up and then I'm just worried about managing everything. How am I gonna deal with everything? So I'd say it's a lot.

Dr. Todd Grande: So it's very... it's very distressing for you.

Sarah: Very much so.

Dr. Todd Grande: And you mentioned it's impacting school?

Sarah: Well in school I'm not doing too well right now. Um, I'm... when I was in undergrad I used to be a straight-A student. I thought I could do it again, just pick up where I left off. But right now I'm worried so much that I'm so focused on worrying... worrying... that I'm worried about what assignment is due, worried about do I have this turned in, that my grades are slipping right now because I'm so... or when I'm in school I'm so worried about home and what's going on at home that I can't pay attention in class. And it's just all-consuming.

Dr. Todd Grande: All right. So both at school and at home.

Sarah: Oh, yes. Definitely.

Dr. Todd Grande: You find it difficult to control the anxiety?

Sarah: Yes.

Dr. Todd Grande: Yeah. And it's affecting you in a major way?

Sarah: Yes. Very much so.

Dr. Todd Grande: I'm going to ask you some other questions that may be tied in with this, okay? Do you use any alcohol or drugs?

Sarah: Some.

Dr. Todd Grande: Some?

Sarah: Like... I have a drink occasionally but I'm so worried right now, my nerves are always on edge right now, that I find it helps. So, I mean I... I've got it under control, but...

Dr. Todd Grande: It's under control?

Sarah: Yeah.

Dr. Todd Grande: How often would you say you drink?

Sarah: Um, maybe some here and there every day.

Dr. Todd Grande: Yeah. And how much would you say you're drinking?

Sarah: Um, maybe a few glasses of wine at night. But I'm not an alcoholic or anything.

Dr. Todd Grande: Okay. How about the drug use?

Sarah: A little pot now and then. But I find it helps my nerves.

Dr. Todd Grande: So just now and then?

Sarah: Um, like maybe a couple times a week.

Dr. Todd Grande: Couple times a week. All right. Have you ever had a panic attack?

Sarah: No.

Dr. Todd Grande: No. Have you ever had any trauma in your history?

Sarah: Well my grandma, she died when I was young. She used to take care of us. She was like a second mom to me and I saw her that way. And she died when I was young, and she was really young. And it just... I was really close to her. And just... I think about her a lot now. Especially since I have started back to school. But I'm thinking about... she's always encouraged me to "get your education, get it while you can," and now just... I've been thinking about her a lot.

Dr. Todd Grande: So she's been on your mind. And when you think about her, what's the feeling that comes up?

Sarah: Um, I worry a lot. Because I'm thinking I'm upsetting her, and her memory. That if I don't do well, then she will be upset. Even though that I know she's not here anymore, she'll be upset if I'm not doing well.

Dr. Todd Grande: All right, so when you... so when you're thinking about her, you're having some... some worry?

Sarah: Yes.

Dr. Todd Grande: That's been distressing you?

Sarah: Very much... yes.

Dr. Todd Grande: All right, so I'm going to ask you some different symptoms. Let me know if you've had these symptoms as part of what's going on now. Okay? Do you feel restless, keyed up, or on edge?

Sarah: All the time.

Dr. Todd Grande: Yeah?

Sarah: Just so tense.

Dr. Todd Grande: How about... do you feel like you get tired easily?

Sarah: I'm tired all the time.

Dr. Todd Grande: Yes?

Sarah: Yes.

Dr. Todd Grande: How about... do you find your mind going blank or having trouble concentrating?

Sarah: Well I find like I'm trying to think of so many things at once so I can't focus just on one thing. So yes, definitely having trouble concentrating.

Dr. Todd Grande: Trouble concentrating. Have you noticed that you were more irritable?

Sarah: Um, I'm not sleeping a lot so I'm cranky.

Dr. Todd Grande: Cranky? So maybe a little bit?

Sarah: Well according to my husband, a lot irritable.

Dr. Todd Grande: Okay. Now you mentioned you're tense all the time. Is that like a muscle tension?

Sarah: Um, pretty much so. Just feel like I... like my muscles are going to snap. Just... I feel so rigid all the time.

Dr. Todd Grande: Okay. And tell me about your sleep.

Sarah: Um, sleep's been... what sleep? It's just like non-existent pretty much right now.

Dr. Todd Grande: Just...

Sarah: Just trying to go to sleep when you have so much on your mind is hard.

Dr. Todd Grande: So you have difficulty falling asleep? How about once you fall asleep? Do you stay asleep?

Sarah: Um, no. Because I find like even though I have nightmares that would just wake me up, and then I just find myself when I get up, "Oh my gosh, what do I have to do? What am I forgetting?" So it's just always feel like there's something always on my mind that just makes it... if I'm asleep I can't stay asleep because I wake up thinking about it. I can't go back to sleep. It's just some ugly cycle going on right now.

Dr. Todd Grande: All right. So sleep has been a big... big problem for you.

Sarah: Yes.

Dr. Todd Grande: Sarah, I'd like to get you in to see a counselor. I can probably get you in to see one in just a couple days if that's okay.

Sarah: Oh, I would appreciate that.

Dr. Todd Grande: That'd be helpful?

Sarah: Yes. Yes.

Dr. Todd Grande: And I want to thank you for answering these questions for me. This has been helpful.

Sarah: No, thank you very much.

Dr. Todd Grande: Thanks, Sarah.
"""
    },

    # =========================================
    # CONVERSATION 6: GAD - Sarah (Subthreshold)
    # =========================================
    {
        "name": "gad_sarah_003",
        "source_description": "Clinical intake - GAD assessment (subthreshold, does not meet full criteria)",
        "diagnosis": "Anxiety symptoms (subthreshold GAD)",
        "meets_criteria": False,
        "notes": "Does not clearly meet 'more days than not' criterion; impairment limited to home; doing well academically and socially",
        "content": """
Dr. Todd Grande: Hi Sarah, how you doing today?

Sarah: Um, hi. I'm doing alright today.

Dr. Todd Grande: Yes. I understand that you've been having some symptoms and that's what has brought you into our agency. Could you tell me about that?

Sarah: Um, I've been having a lot of worry.

Dr. Todd Grande: A lot of worry?

Sarah: Yes, a lot of worry on and off for about the past four or five months. Maybe four or five months... maybe about six months. Yeah, around four, five, six months. And I just started back to school after being a stay-at-home mom for 20 years. The kids are all off to college now and away, and I decided why not go back to school? Do something else now. And it's just been causing... and I've just been worrying so much lately.

Dr. Todd Grande: All right, so... so a lot of worry. Somewhere at four or five or six months it's been going on. Somewhere in there, four, five, six months. Have you had this worry more days than you haven't had it in that last four to six months?

Sarah: I've had a lot of good days. Hmm. I mean I've had some bad days but I've had a lot of good days too. So... um, I don't know.

Dr. Todd Grande: Okay. Not quite sure?

Sarah: Not sure.

Dr. Todd Grande: Do you find the worry difficult to control?

Sarah: Um, when I do worry, yes. Yes.

Dr. Todd Grande: So I'm going to ask you some questions related to this. Let me know if you've experienced these symptoms. Do you feel restless, keyed up, or on edge?

Sarah: Yes. Yes, I do.

Dr. Todd Grande: Okay. How about... are you easily tired all the time?

Sarah: So tired all the time. Yeah.

Dr. Todd Grande: All the time. Yes?

Sarah: Yes.

Dr. Todd Grande: Do you have trouble concentrating or finding your mind go blank?

Sarah: I find my mind is wandering. Just going blank... I would call that going blank, yes.

Dr. Todd Grande: Hmm. Okay. Do you find that you've been irritable?

Sarah: Very much so. Yeah.

Dr. Todd Grande: Any muscle tension?

Sarah: Yes. Just rigidness.

Dr. Todd Grande: And tell me about how you've been sleeping.

Sarah: Um, not very well. I would say not very well lately. Find it hard... just I can't go to sleep and I can't stay asleep. It's just been hard.

Dr. Todd Grande: Do you drink alcohol or use any drugs?

Sarah: No, I don't.

Dr. Todd Grande: No. Have you ever had a panic attack?

Sarah: No.

Dr. Todd Grande: Any trauma in your history?

Sarah: No.

Dr. Todd Grande: Any mental health disorders at all?

Sarah: No.

Dr. Todd Grande: You find the symptoms very distressing?

Sarah: Um, yes. Distressing, yes.

Dr. Todd Grande: In what areas are they distressing?

Sarah: Um, at home. So much at home. Yeah. Like I'm doing... I'm doing great in school. School's okay. School's... got a 4.0.

Dr. Todd Grande: Wow. Very good.

Sarah: Um, just at home I'm just in a constant state of worry all the time.

Dr. Todd Grande: How about when you go out with friends?

Sarah: Have fun. Great times with my friends. Love going out.

Dr. Todd Grande: Is there something specific to your home environment you think might be contributing to this because you don't have it at school, you don't have it socially?

Sarah: Yeah. I mean we have some problems here and there. Some problems here and there. Mmm.

Dr. Todd Grande: Nothing you could isolate as maybe causing these symptoms?

Sarah: Um, maybe... maybe not. Just nothing I can't... nothing you can't work through.

Dr. Todd Grande: All right, Sarah. I'm gonna get you in to see one of our counselors if that's okay with you. Just take a couple days for you to get in... get an appointment set for you to get in. Is that okay?

Sarah: I'd like that. Yes.

Dr. Todd Grande: Okay. I'll get that set up. And I want to thank you for answering these questions. It's very helpful to me.

Sarah: Thank you.

Dr. Todd Grande: Thanks Sarah.
"""
    },

    # =========================================
    # CONVERSATION 7: Wernicke's Aphasia - Byron
    # =========================================
    {
        "name": "wernickes_aphasia_byron_001",
        "source_description": "Interview demonstrating Wernicke's (fluent) aphasia",
        "diagnosis": "Wernicke's Aphasia",
        "meets_criteria": True,
        "notes": "Demonstrates fluent but nonsensical speech, paraphasias, neologisms, and poor comprehension characteristic of Wernicke's aphasia",
        "content": """
Interviewer: Hi Byron, how are you?

Byron: I'm happy. Are you pretty? You look good.

Interviewer: What are you doing today?

Byron: We stayed with the water over here at the moment and talk with the people of them over there. They're diving for them at the moment. They'll save in the moment. He'll have water very soon for him. With luck for him.

Interviewer: So we're on a cruise... and we're about to...

Byron: We will s... right here and they'll save their hands right there for them.

Interviewer: And what were we just doing with the iPad?

Byron: Uh, right at the moment they don't show a darn thing.

Interviewer: With the iPad that we were doing. Like here?

Byron: I'd like my change for me and change hands for me. It was happening. I would talk with Donna sometimes. We're out with them. Other people are working with them of them. I'm very happy with them.

Interviewer: Good.

Byron: This girl was very good. And happy. I might play golf and hit other trees. We play out with the hands. We save a lot of hands on hold for people's for us. Other hands. I don't know what you get but I talk with a lot of hand for him. Sometime. Am I talk of any more to saying.

Interviewer: All right. Thank you very much.

Byron: Thank you very much. I appreciate it. And I hope the world lasts for you.

Interviewer: Thank you. It's been a pleasure. Bye bye.

Byron: Yeah.
"""
    },
]


# Summary statistics for the dataset
DATASET_SUMMARY = """
Empirical Conversations Dataset Summary
=======================================

Source: Dr. Todd Grande clinical demonstration videos

Conditions Represented:
- Generalized Anxiety Disorder (GAD): 3 conversations
  - 2 meeting DSM-5 criteria (1 with comorbidities)
  - 1 subthreshold/not meeting criteria
  
- ADHD: 3 conversations
  - 2 meeting criteria (combined presentation)
  - 1 not meeting criteria (inattention only, few hyperactive symptoms)
  
- Wernicke's Aphasia: 1 conversation
  - Demonstrates fluent aphasia characteristics

Key Features:
- Real diagnostic interview structure
- DSM-5 criteria systematically assessed
- Differential diagnosis demonstrated
- Comorbidity screening included
- Functional impairment assessment
- Both threshold and subthreshold presentations
"""


# DSM-5 criteria mapped in these conversations
DSM5_CRITERIA_DEMONSTRATED = {
    "GAD": {
        "A": "Excessive anxiety and worry occurring more days than not for at least 6 months",
        "B": "Difficulty controlling the worry",
        "C": "Associated with 3+ of: restlessness, fatigue, concentration problems, irritability, muscle tension, sleep disturbance",
        "D": "Causes clinically significant distress or impairment",
        "E": "Not attributable to substances or medical condition",
        "F": "Not better explained by another mental disorder"
    },
    "ADHD": {
        "Inattention": [
            "Fails to give close attention / careless mistakes",
            "Difficulty sustaining attention",
            "Does not seem to listen when spoken to directly",
            "Does not follow through on instructions",
            "Difficulty organizing tasks",
            "Avoids tasks requiring sustained mental effort",
            "Loses things necessary for tasks",
            "Easily distracted",
            "Forgetful in daily activities"
        ],
        "Hyperactivity-Impulsivity": [
            "Fidgets or squirms",
            "Leaves seat when remaining seated expected",
            "Runs/climbs inappropriately (restlessness in adults)",
            "Unable to engage in leisure activities quietly",
            "On the go / driven by a motor",
            "Talks excessively",
            "Blurts out answers",
            "Difficulty waiting turn",
            "Interrupts or intrudes on others"
        ],
        "Additional_criteria": [
            "Several symptoms present before age 12",
            "Symptoms present in 2+ settings",
            "Clear evidence of functional impairment",
            "Not better explained by another disorder"
        ]
    }
}
