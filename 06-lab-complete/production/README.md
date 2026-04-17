# Production

Production environment for Railway.

## Railway

1. Create new project.
2. root directory `06-lab-complete/production`.
3. Set env vars `.env.example`then copy to `.env`.
4. Railway is built by `Dockerfile` and read `railway.toml`.

5. docker build -t streamlit-prod .
6. docker run --env-file .env -p 8080:8080 streamlit-prod
7. railway init (or railway link)
8. railway service (remember to set API_KEY, JWT_SECRET, JWT_EXP_MINUTES, ADMIN_USERNAME, ADMIN_PASSWORD, USER_USERNAME, USER_PASSWORD)
9. railway up
10. railway domain