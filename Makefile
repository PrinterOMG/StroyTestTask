up_dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

down_dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

up_prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build

down_prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down
