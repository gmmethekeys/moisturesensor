echo "Starting email notification script..."

while :
do
    now=$(date +"%T")
    python notification_reminder.py
    echo "Script was ran at $now."
    echo "Sleeping 1 day."
    sleep 1d
done
