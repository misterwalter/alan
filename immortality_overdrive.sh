while :; do
    git pull
    pipenv run python3 Alan.py
    echo "Alan has fallen!"
    date
    sleep 1
    echo "Engage Immortality Overdrive!"
done
