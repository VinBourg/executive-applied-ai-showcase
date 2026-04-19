# SQL Decision Support Report

This report shows how a compact SQL layer can produce segment visibility, account-risk reading and a business action queue.

## Revenue by segment
Shows where revenue concentration sits and whether adoption quality supports that value.

```sql
select segment,
                   round(sum(monthly_revenue), 2) as total_revenue,
                   round(avg(adoption_score), 1) as avg_adoption_score
            from accounts
            group by segment
            order by total_revenue desc;
```

| segment | total_revenue | avg_adoption_score |
| --- | --- | --- |
| Banking | 89000.0 | 61.0 |
| AgriFood | 57000.0 | 56.0 |
| Insurance | 39000.0 | 76.0 |
| Retail | 22000.0 | 71.0 |

## Accounts at risk
Identifies accounts where usage decline, service pressure or weak adoption should trigger a coordinated review.

```sql
select company_name,
                   segment,
                   usage_drop_pct,
                   open_support_tickets,
                   adoption_score,
                   renewal_window_days
            from accounts
            where usage_drop_pct >= 20
               or open_support_tickets >= 2
               or adoption_score <= 60
            order by usage_drop_pct desc, open_support_tickets desc, renewal_window_days asc;
```

| company_name | segment | usage_drop_pct | open_support_tickets | adoption_score | renewal_window_days |
| --- | --- | --- | --- | --- | --- |
| AgriNova | AgriFood | 35.0 | 3 | 44 | 18 |
| AtlasPay | Banking | 28.0 | 2 | 64 | 55 |
| Northbank | Banking | 8.0 | 1 | 58 | 45 |

## Priority follow-up queue
Turns raw account signals into an action queue a business team can immediately own.

```sql
select company_name,
                   segment,
                   case
                       when usage_drop_pct >= 25 and open_support_tickets >= 2 then 'urgent review'
                       when adoption_score <= 55 then 'adoption recovery'
                       when renewal_window_days <= 30 and usage_drop_pct >= 10 then 'renewal stabilization'
                       when open_support_tickets >= 2 then 'support stabilization'
                       else 'monitor'
                   end as recommendation,
                   renewal_window_days
            from accounts
            order by
                case
                    when usage_drop_pct >= 25 and open_support_tickets >= 2 then 1
                    when adoption_score <= 55 then 2
                    when renewal_window_days <= 30 and usage_drop_pct >= 10 then 3
                    when open_support_tickets >= 2 then 4
                    else 5
                end,
                renewal_window_days asc;
```

| company_name | segment | recommendation | renewal_window_days |
| --- | --- | --- | --- |
| AgriNova | AgriFood | urgent review | 18 |
| AtlasPay | Banking | urgent review | 55 |
| FlowRetail | Retail | renewal stabilization | 27 |
| PureFoods | AgriFood | monitor | 24 |
| Northbank | Banking | monitor | 45 |
| SwissAdvisory | Insurance | monitor | 61 |

## What This Demonstrates
This example shows SQL used as a business decision tool: summarize value, detect risk and produce an actionable follow-up queue.
