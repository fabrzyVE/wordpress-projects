---
name: risk-analyzer
description: a skill to help analyze the risks of deploying local work into production wordpress site. Use this whenever the intention is to deploy local work
--- 

# Risk Analyzer 

When the user asks to deploy local facing work to production, follow these steps:

1. Analyze the process of deploying to production wordpress site
2. Check if work modifies / deletes any existing content and confirm with the user
3. Prefer if deployment is done with work being pushed in draft mode rather than published
4. Make sure the work being deployed doesn't impact the website negatively in anyway
5. Quality check if the work will be functional once viewed from the production site 

If all criteria passes , you may give the green light to deploy
