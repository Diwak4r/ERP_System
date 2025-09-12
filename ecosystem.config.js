module.exports = {
  apps: [{
    name: 'erp-system',
    script: 'python',
    args: 'app.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PORT: 5000,
      FLASK_APP: 'app.py',
      FLASK_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};