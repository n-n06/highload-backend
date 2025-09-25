## Task 1 Answers

### Как выбор структуры базы данных (SQL или NoSQL) влияет на дизайн CRUD API? 
In general, the main difference between SQL and NoSQL (which means Not only SQL) DB is the fact that SQL DBs store data in tables, while NoSQL DBs in document, key-value, column-family, or graph-based structures. Tables are usually defined with a rather strict/fixed schema, while NoSQL DBs support dynamic schemas, This means, that when designing CRUD API we have more flexibility when working with data. For example, when working with document based DBs, it is esay to define new parameters (keys), while in SQL DBs we have to add an additional column for that.

Also, we might integrate some complex join operations for some of our GET endpoints. SQL supports joins, while it is difficult to do with NoSQL DBs. So, when designin a CRUD API we have to keep that in mind. However, since data in NoSQL DBs like Mongo can be nested - we might not need joins, as we might store the necessary data in 1 object. For example, in an SQL DB we would have to join orders and products to see the products in an order for an endpoint like `GET /orders/:id/products`, while the products might be stored in the orders itself, so that we would get them by using `GET /orders/:id`. So, in the end, the GET operations might be easier for NoSQL DBs

If we have an UPDATE endpoint, it might be tricky to do with NoSQL DBs are there might be duplicates in several objects, while it is fairly simple in SQL DBs (assuming of course that our SQL DB is normalized up to 3NF and has no redundancy). So, SQL DBs are better for updates, fine-grained reads.

Also, SQL is a mostly standardized language that is almost the same for various RDBMS systems. NoSQL, on the other hand, differs in this aspect, as different NoSQL DBs have different ways query patterns. So, changing the DB in the middle of creating an API might be more of a problem when using NoSQL.

In general, when we design a CRUD API, we have to consider what are our main goals - a fine-grained control, where there is no redundancy, fixed schema and also transactions OR a fast, larger-grained, eventually consistent view of data.

### Какие проблемы могут возникнуть при массовых обновлениях данных через API? 
- Overload of network, database, server and everything else 
- DB objects get locked (if transactions are present) and other users can't access it
- Risk of inconsistent or weird data if transactions are not set up (no transactions in SQL or using NoSQL)
- Potential timeouts
- Hard to monitor batch updates - too much logs :(

Couple of solutions (from a Habr article):
- batch endpoint - can put everything into 1 transaction, reduces network congestion and number of HTTP connections. However, it would be harder to parse the response object, and we would have to handle elements separately (status code 207 and separate reports)
- async hadnling - does not block http brokers, reduces strain on the system. Requires msg broker and background tasks handler (Celery with Redis). Client has to wait for the answer 


### Почему важно использовать правильные HTTP-методы (GET, POST, PUT, DELETE), а не только POST? 
I think it is important to use HTTP methods as they are intended for several reasons
- self-documentation / semantic methods - the name of the method tells the user what type of operation this endpoint provides. The rules for HTTP methods are standardized, so this would make communication between back/front teams easier, and would make the API more intuitive and predictable. I think it is the same as using `<header>`, `<article>`, `<footer>` in HTML instead of `div`s with a lot of ids and class names. This provides a general understanding of the code without even looking deep into it.
- browsers cache GET requests, so usign POST everywhere would make the API slower
- PUT and DELETE methods guarantee idempotency (press the button 10 times in a row, but get the same result). If we use POST everywhere, we lose this

