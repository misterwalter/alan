while :; do
    git pull
    pipenv run Alan.py;
    echo "Alan has fallen!";
    date;
    sleep 1;
    echo "Engage Immortality Overdrive!";
done
