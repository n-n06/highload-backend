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


## Task 2 Answers
### Какие уязвимости могут возникнуть при хранении JWT на клиентской стороне? 
- JWT cannot be invalidated before its expiry date. If a token is ever compromised or a user needs to be disconnected immediately, it will be required to:
    - sep up a server side blacklist
    - wait for the JWT to expire, which can cause security issues
- If an attacker gets the JWT and the token is not verified. In this case, it is easy for the attacker to modify the content of the payload. For example, using a different role like 'admin'.  
- An attacker can simply modify the JOSE header of the JWT, replace the alg field with none, and then freely alter the contents of the token (for example, by giving himself administrator privileges). All without the need for a valid signature.
- It is possible to brute force the JWT secret and compromise every token if the secret is too easy. 
- Not good for sessions.


### В каких случаях стоит ограничивать время жизни JWT, и какие проблемы это создаёт для UX? 
- better to use short lived JWT in any case, as it cannot be invalidated before its expire date
- in apps that can include things like frequent changes to user permissions

When using short lifespans for JWT tokens, the UX can get worse, as users would have to relogin ofter. There is also a chance that if a user goes offlie for a long time, he/she would not be able to refresh their token.  

### Как логирование помогает в расследовании инцидентов безопасности? 
- all of the actions of the users are recorded, so it is easy to see who did what
- because we use logging with payloads, we can see every request body
- with configured visualization like Kibana it is easy to track the number of different requests which can help identify security attacks like DDoS.

## Task 3 Answers
### В чём разница между горизонтальным и вертикальным масштабированием, и как это связано с кэшированием? 
Horizontal scaling is increasing the number of computing instances - wether it is VMs in a network, nodes in a cluster. This allows to distribute the workload across a larger number of individual units. Horizontal scaling is great as it has little to no downtime, provides increased capacity, improved performance (workload is distributed among machines or servers). However, there are also some downsides, like maintaining consistency across nodes, increased networking and power consumption, more complex management.

Vertical scaling is increasing the capacity or capabilities of an individual hardware or software component within a system. Instead of adding new instances, we upgrade existing ones with better processors, increased RAM, etc. Vertical scaling provides increased capacity with easier maintenance, as only node needs to be managed.
### Какой риск несут фоновые задачи при сбое очереди сообщений? 
Background tasks pose several risks in case of a message queue failure
- tasks may be lost permanently, if replication, partitioning or other durability measures have NOT been setup.
- when the queue is restored or messages are resent, there is a risk that the same tasks will be executed multiple times, and in some cases, like processing money transactions or managing expensive inventory, it might cause big trouble for the business.

### Почему важно учитывать идемпотентность задач при их повторном выполнении? 
Idempotency - performing an actions several times produces the same result as if it was processed only once. 
It is important to account for idempotency when handling retrues for several reasons:
- first, handling retries. Retries after failures are common in distributed systems, so it is important that retries are idempotent to avoid data corruption or inconsistent state of the system
- second, most message queue or event streaming systems like RabbitMQ, Kafka and others have at-least-once deliery semantics. So, it is possible to overlook this fact and setup 1 action per some message or event; however, it is best to check for duplicates before triggering processing to ensure that this event/message has not been processed yet.
- third, most distributed systems function in clusters and scale horizontally. In case of a failure, another node might pick up the failed task and retry its processing. It is best to ensure that when the task is picked up, it is processed idempotently.
- forth, when updating caches or external systems, repeated updates should not lead to inconsistent data. Idempotent operation guarantee that data will no be left in an inconsistent state.
- fifth, idempotency prevents users from accidentally triggering duplicate actions due to page reloads or network issues.
- sixth, idempotent operations makes it easier to track and audit system actions.

## Task 4 Answers
### Что сложнее поддерживать в большой системе: код или документацию? Почему? 
I think it is harder to maintain the documentation rather than the code because describing created functionality in a comprehensive and easy to understand manner is challenging. Everyone might interprets sentences and words of a documentation differently. Also different people might have different approaches to documentation process, and this process might be more difficult to standardize across the organization, which might result in a very messy documentation.

Code, on the other hand, is the key part of the system, and it really isn't easy to maintain. However, specifying rules related to code style, architectural and other patterns is easier, as this type of specification is more concrete and less abstract, and easier to understand for technical people.

### Какие плюсы и минусы у ручного написания README по сравнению с автогенерацией документации? 
Writing documentation by hand has several pros:
- documenting the real intent / idea of the programmer
- flexibility of documentation process - it is possible to add as many details as the developer considers necessary
- possibility to add more engaging contents. It might be possible that to facilitate understanding the developer decides to ass some more engaging and fun aspects to the documentation. These elements would be impossible to implement in an auto-genetared docs.

Cons:
- amount of work
- inconsistent writing styles inside the developing team.\

### Как документация помогает при онбординге новых разработчиков в команду? 
Documentation helps during the onboarding of new developers by
- providing clear explanations of the system’s architecture, workflows, coding standards and setup instructions
- answering common questions, making onboarding smoother and less time consuming
