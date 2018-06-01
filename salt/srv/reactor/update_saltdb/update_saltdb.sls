update salt db:
    runner.minionrecord.update:
        - url: http://vmsaltdb-01.dev.scl1.us.tribalfusion.net:9200
        - index: devsalt
        - data: {{ data }}
