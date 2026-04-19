# Copilot Report - AI SQL Analytics Copilot

This document shows how a compact copilot can translate business questions into SQL and decision-oriented answers.

## Question 1
Which accounts need immediate review because revenue is contracting while support pressure stays high?

**Intent:** `risk_review`
**View:** Accounts requiring immediate review
**Decision owner:** Customer success and operations lead
**Priority:** `high`

### Generated SQL
```sql
select company_name,
                       industry,
                       revenue_growth_pct,
                       open_tickets,
                       product_adoption_pct,
                       case
                           when revenue_growth_pct <= -10 and open_tickets >= 3 then 'urgent retention review'
                           when revenue_growth_pct < 0 and open_tickets >= 2 then 'stabilize account'
                           when product_adoption_pct < 60 then 'adoption recovery plan'
                           else 'monitor'
                       end as recommendation
                from account_metrics
                where revenue_growth_pct < 0
                   or open_tickets >= 3
                   or product_adoption_pct < 60
                order by revenue_growth_pct asc, open_tickets desc;
```

### Result
| company_name | industry | revenue_growth_pct | open_tickets | product_adoption_pct | recommendation |
| --- | --- | --- | --- | --- | --- |
| AgriNova | AgriFood | -14.0 | 3 | 54.0 | urgent retention review |
| Northbank | Banking | -8.0 | 4 | 58.0 | stabilize account |
| TerraRetail | Retail | -6.0 | 2 | 61.0 | stabilize account |
| FlowRetail | Retail | 3.0 | 4 | 69.0 | monitor |

### Business Interpretation
The copilot should isolate accounts combining contraction, operational friction and weak adoption because these are the accounts most likely to need coordinated action.

### Copilot Summary
Immediate attention should start with AgriNova, where revenue contraction and ticket pressure overlap.

### Recommended Actions
- Launch retention reviews first on accounts with both negative growth and high ticket volume.
- Separate support stabilization from adoption recovery so the action plan stays clear.

### Operating Note
- Next step: Run a joint retention and service review on the flagged accounts.
- Top signal: AgriNova combines -14.0% growth with 3 open tickets.

## Question 2
Which industries generate the most revenue but also show operational support pressure?

**Intent:** `segment_pressure`
**View:** Revenue concentration versus support pressure by industry
**Decision owner:** Segment operations director
**Priority:** `high`

### Generated SQL
```sql
select industry,
                       round(sum(monthly_revenue_k), 1) as total_revenue_k,
                       round(avg(open_tickets), 1) as avg_open_tickets,
                       round(avg(revenue_growth_pct), 1) as avg_growth_pct,
                       round(avg(nps), 1) as avg_nps,
                       sum(case when open_tickets >= 3 then 1 else 0 end) as stressed_accounts
                from account_metrics
                group by industry
                order by total_revenue_k desc, avg_open_tickets desc;
```

### Result
| industry | total_revenue_k | avg_open_tickets | avg_growth_pct | avg_nps | stressed_accounts |
| --- | --- | --- | --- | --- | --- |
| Banking | 1250.0 | 2.3 | 3.3 | 56.7 | 1 |
| Insurance | 600.0 | 1.5 | 8.0 | 64.0 | 0 |
| Retail | 445.0 | 3.0 | -1.5 | 50.5 | 1 |
| AgriFood | 390.0 | 2.0 | -5.0 | 48.0 | 1 |
| Industry | 330.0 | 1.0 | 15.0 | 71.0 | 0 |

### Business Interpretation
The copilot should show where revenue concentration and support strain overlap, because this is where operational pressure can threaten the most value.

### Copilot Summary
Banking is the largest revenue segment in this sample while still showing 2.3 average open tickets, which makes it the first segment to protect operationally.

### Recommended Actions
- Protect high-revenue industries first when support pressure rises.
- Use stressed-account counts to prioritize targeted service reviews by segment.

### Operating Note
- Next step: Protect the most exposed segment with targeted service and account coverage actions.
- Top signal: Banking concentrates 1250.0k revenue with 2.3 average open tickets.

## Question 3
Where should we focus expansion efforts based on adoption and pipeline strength?

**Intent:** `growth_focus`
**View:** Expansion priorities from adoption and pipeline strength
**Decision owner:** Growth and account expansion lead
**Priority:** `medium`

### Generated SQL
```sql
select company_name,
                       industry,
                       pipeline_value_k,
                       product_adoption_pct,
                       revenue_growth_pct,
                       nps,
                       case
                           when pipeline_value_k >= 120 and product_adoption_pct >= 75 and nps >= 60 then 'prioritize expansion'
                           when pipeline_value_k >= 90 and product_adoption_pct >= 70 then 'qualified growth opportunity'
                           else 'prepare before expansion'
                       end as recommendation
                from account_metrics
                order by pipeline_value_k desc, product_adoption_pct desc, nps desc;
```

### Result
| company_name | industry | pipeline_value_k | product_adoption_pct | revenue_growth_pct | nps | recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| Machina Systems | Industry | 160.0 | 84.0 | 15.0 | 71.0 | prioritize expansion |
| AtlasPay | Banking | 140.0 | 82.0 | 12.0 | 67.0 | prioritize expansion |
| Swiss Advisory Tech | Insurance | 130.0 | 79.0 | 9.0 | 65.0 | prioritize expansion |
| NordLedger Insurance | Insurance | 120.0 | 74.0 | 7.0 | 63.0 | qualified growth opportunity |
| Alpine Payments | Banking | 95.0 | 76.0 | 6.0 | 62.0 | qualified growth opportunity |
| FlowRetail | Retail | 85.0 | 69.0 | 3.0 | 52.0 | prepare before expansion |
| Northbank | Banking | 60.0 | 58.0 | -8.0 | 41.0 | prepare before expansion |
| TerraRetail | Retail | 50.0 | 61.0 | -6.0 | 49.0 | prepare before expansion |
| PureFoods | AgriFood | 48.0 | 71.0 | 4.0 | 58.0 | prepare before expansion |
| AgriNova | AgriFood | 25.0 | 54.0 | -14.0 | 38.0 | prepare before expansion |

### Business Interpretation
The copilot should identify expansion candidates with both commercial headroom and strong product footing, rather than relying on pipeline alone.

### Copilot Summary
Expansion effort should concentrate first on Machina Systems, AtlasPay, Swiss Advisory Tech.

### Recommended Actions
- Focus growth effort on accounts combining strong pipeline, adoption and sentiment.
- Keep weaker-adoption accounts in enablement mode before pushing expansion motions.

### Operating Note
- Next step: Prioritize the best expansion candidates and keep weaker adoption accounts in enablement mode.
- Top signal: Machina Systems leads with 160.0k pipeline and 84.0% adoption.

