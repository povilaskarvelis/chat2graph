"""
Sample conversation datasets for testing the knowledge graph pipeline.

These simulate different types of conversations you might want to analyze:
- Team discussions
- Customer support
- Meeting notes
- Project updates
"""

CONVERSATIONS = [
    # =========================================
    # CONVERSATION 1: Product Team Discussion
    # =========================================
    {
        "name": "product_team_chat",
        "source_description": "Product team Slack channel",
        "content": """
Emma: Hey team, just got off a call with DataFlow Inc. They're interested in our enterprise plan!

Marcus: That's great! Who did you talk to there?

Emma: Their CTO, Dr. Rebecca Torres. She's really sharp - used to lead the ML team at Google 
before joining DataFlow last year.

Marcus: Nice connection. What's their main use case?

Emma: They want to integrate our API into their analytics platform. Rebecca mentioned they're 
processing about 10 million events per day and need better real-time insights.

Sophie: That's significant volume. Did she mention their timeline?

Emma: They want to pilot in Q2, full rollout by Q3. Rebecca is bringing in their Head of 
Engineering, James Park, for the technical deep-dive next week.

Marcus: Perfect. I'll loop in our solutions architect, Nina Chen, for that call.

Sophie: Also, DataFlow is backed by Sequoia Capital, right? Their CEO Michael Zhang was 
featured in TechCrunch last month talking about their Series B.

Emma: Exactly! $45 million round. They're growing fast - just opened offices in Austin and Berlin.
"""
    },
    
    # =========================================
    # CONVERSATION 2: Customer Support Thread
    # =========================================
    {
        "name": "support_ticket_4521",
        "source_description": "Customer support ticket #4521",
        "content": """
Customer (Lisa Wang, Nexus Systems): We're experiencing API timeouts on the /analytics endpoint. 
Started happening yesterday around 3pm PST.

Support Agent (Tom): Hi Lisa, thanks for reporting this. I see Nexus Systems is on our Pro plan 
with the US-West region. Let me check our logs.

Tom: I found the issue - there was a configuration change pushed by our infrastructure team 
that affected routing in US-West. Our DevOps lead, Alex Rivera, is working on a fix.

Lisa Wang: Thanks Tom. This is affecting our client dashboard. Our VP of Product, Karen Chen, 
is asking for an ETA.

Tom: Alex says the fix will be deployed within 2 hours. I'll also CC your account manager, 
David Kim, so he's aware.

Lisa Wang: Appreciated. Also, can you send the incident report to our compliance team? 
Contact is Robert Martinez at compliance@nexussystems.com.

Tom: Will do. I'll have our reliability engineer, Priya Sharma, prepare the report. She handles 
all our SOC 2 documentation.

Lisa Wang: Perfect. Karen will want to review it for our board meeting next Tuesday.
"""
    },
    
    # =========================================
    # CONVERSATION 3: Startup Founders Chat
    # =========================================
    {
        "name": "founders_chat",
        "source_description": "Private founders WhatsApp group",
        "content": """
Alex: Just had coffee with Sarah Miller from Andreessen Horowitz. She's interested in leading 
our Series A!

Jordan: That's huge! Sarah led the Figma investment back in the day.

Alex: Yeah, she's incredibly well-connected. Introduced me to her partner, Chris Lee, who 
focuses on B2B SaaS.

Taylor: Did you mention we're talking to Accel too?

Alex: Yes, told her we're in conversations with Miles Chen at Accel. She respects him - they 
co-invested in Notion together.

Jordan: What about the strategic investors? I thought Salesforce Ventures was interested.

Alex: They are! Jessica Wong from Salesforce Ventures reached out. She used to work with our 
advisor, Mark Thompson, at Oracle.

Taylor: Mark's connections are gold. He introduced us to half of Silicon Valley.

Alex: Speaking of which, he wants us to meet Bill Roberts, the founder of CloudScale. They 
exited for $2B last year and Bill is now angel investing.

Jordan: Perfect. Let's also loop in our board member, Linda Park. She has context on all these relationships.
"""
    },
    
    # =========================================
    # CONVERSATION 4: Research Collaboration
    # =========================================
    {
        "name": "research_collab",
        "source_description": "Research team email thread",
        "content": """
Dr. Chen: Team, I've been in touch with Professor Emily Watson at MIT. Her lab published that 
breakthrough paper on transformer efficiency that we've been discussing.

Dr. Patel: Emily's work is excellent! I met her at NeurIPS last year. She's collaborating 
with Professor Yuki Tanaka at Stanford on a follow-up.

Dr. Chen: Exactly. Emily mentioned Yuki might be interested in a joint research project with us.
She's also working with DeepMind - specifically with their research director, Dr. James Liu.

Dr. Martinez: James Liu? He was my PhD advisor at Berkeley! Small world.

Dr. Chen: That's a great connection. Emily also suggested we apply for the NSF grant together.
The program officer, Dr. Michelle Brown, is looking for industry-academic collaborations.

Dr. Patel: I know Michelle from my time at DARPA. She's very supportive of AI safety research.

Dr. Martinez: Should we also reach out to Dr. Robert Kim at Google Brain? His team is doing 
similar work on model compression.

Dr. Chen: Good idea. Robert presented at our workshop last month. His manager, VP of Research 
Dr. Sarah Anderson, is pushing for more academic partnerships.
"""
    },
    
    # =========================================
    # CONVERSATION 5: Marketing Campaign Planning
    # =========================================
    {
        "name": "marketing_planning",
        "source_description": "Marketing team standup notes",
        "content": """
Rachel: Alright team, let's plan the Q2 campaign. Our main target is enterprise decision-makers 
in the fintech space.

Mike: I've been talking to Jennifer Walsh at Bloomberg. She's their Head of Developer Relations 
and interested in a co-marketing opportunity.

Rachel: Perfect. Jennifer has great reach. What about the conference circuit?

Amanda: I got us a speaking slot at FinTech Summit in NYC. The organizer, David Chen, also 
offered us a booth if we want it.

Mike: David's events are always well-attended. Last year, CEOs from Stripe, Plaid, and Square 
were all there.

Rachel: Speaking of Stripe, I had a call with their marketing director, Lisa Park. She might 
feature us in their partner showcase.

Amanda: That would be huge exposure. We should also reach out to the TechCrunch team - their 
fintech reporter, Kevin Martinez, covered our competitor last month.

Mike: I know Kevin! He interviewed our CEO, Sarah, at Disrupt last year. Let me reconnect.

Rachel: Great. Also, our investor, Maria Santos from Index Ventures, offered to introduce us 
to her portfolio companies for case studies.

Amanda: Maria's portfolio includes three unicorns in fintech. Those would be amazing references.
"""
    },
]

# Simpler test dataset for quick testing
QUICK_TEST = {
    "name": "quick_test",
    "source_description": "Quick test conversation",
    "content": """
John: Did you hear? Apple is acquiring TechStartup for $500 million.
Sarah: Wow! That's huge. Tim Cook must really want their AI team.
John: Exactly. TechStartup's CEO, Maria Garcia, built an amazing computer vision platform.
Sarah: I worked with Maria at Stanford. She's brilliant.
John: Their lead researcher, Dr. Lee, is probably the real prize. 
He has 50 patents in neural networks.
"""
}
