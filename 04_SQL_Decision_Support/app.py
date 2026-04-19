import sqlite3


def setup_database(connection):
    cursor = connection.cursor()
    cursor.executescript(
        """
        create table accounts (
            account_id integer primary key,
            company_name text,
            segment text,
            monthly_revenue real,
            usage_drop_pct real,
            open_support_tickets integer
        );

        insert into accounts (company_name, segment, monthly_revenue, usage_drop_pct, open_support_tickets) values
            ('Northbank', 'Banking', 42000, 8, 1),
            ('AgriNova', 'AgriFood', 31000, 35, 3),
            ('FlowRetail', 'Retail', 22000, 12, 0),
            ('AtlasPay', 'Banking', 47000, 28, 2),
            ('PureFoods', 'AgriFood', 26000, 6, 1);
        """
    )
    connection.commit()


def print_query(connection, title, query):
    print(title)
    print("-" * len(title))
    for row in connection.execute(query):
        print(row)
    print()


def main():
    connection = sqlite3.connect(":memory:")
    setup_database(connection)

    print_query(
        connection,
        "Revenue by segment",
        """
        select segment, round(sum(monthly_revenue), 2) as total_revenue
        from accounts
        group by segment
        order by total_revenue desc;
        """,
    )

    print_query(
        connection,
        "Accounts at risk",
        """
        select company_name, segment, usage_drop_pct, open_support_tickets
        from accounts
        where usage_drop_pct >= 25 or open_support_tickets >= 2
        order by usage_drop_pct desc, open_support_tickets desc;
        """,
    )

    print_query(
        connection,
        "Priority follow-up list",
        """
        select company_name,
               case
                   when usage_drop_pct >= 25 and open_support_tickets >= 2 then 'urgent review'
                   when usage_drop_pct >= 20 then 'usage recovery plan'
                   when open_support_tickets >= 2 then 'support stabilization'
                   else 'monitor'
               end as recommendation
        from accounts
        order by recommendation desc;
        """,
    )


if __name__ == "__main__":
    main()
