# Deployment & Rollback Strategy

## Deployment Procedure (Zero Downtime)
We use a Blue/Green deployment strategy using Nginx + Gunicorn/uWSGI.

1. **Environment Preparation**
   - Pull the latest code to the `app_green` directory.
   - Install dependencies: `pip install -r requirements.txt`
   - Run database migrations (schema updates are backward compatible).

2. **Start Green Instance**
   - Start the new application instance on an alternate port (e.g., 5001).
   - Perform health checks: `curl -f http://localhost:5001/`

3. **Switch Traffic**
   - Update Nginx upstream configuration to point to port 5001.
   - Reload Nginx: `sudo nginx -s reload`
   - The traffic is now smoothly transitioned without dropped requests.

4. **Decommission Blue Instance**
   - Stop the old Gunicorn process.

## Rollback Procedure
If critical errors are detected within 5 minutes of deployment:

1. **Revert Traffic**
   - Revert Nginx upstream to point back to the original port (e.g., 5000).
   - Reload Nginx: `sudo nginx -s reload`

2. **Database Reversion**
   - Since schema changes are additive (adding tables/columns), rolling back the code will simply ignore the new columns. No data loss occurs.

3. **Investigation**
   - Check `operation_logs` and application logs to identify the root cause.