#!/bin/bash

FUSEKI_URL="http://127.0.0.1:3030"
DATASET_NAME="OBD"
BACKUP_DIR="knowledge_base/live_kg_backups"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +\%Y\%m\%d_\%H\%M\%S).nt"
KG_SNAPSHOT_FILE="$BACKUP_DIR/kg_snapshot_$(date +\%Y\%m\%d_\%H\%M\%S).txt"

# construct URL for backup request
BACKUP_URL="$FUSEKI_URL/$DATASET_NAME/data?graph=default"

# trigger backup using curl
curl -H "Accept: application/n-triples" "$BACKUP_URL" > $BACKUP_FILE

# check HTTP response code to ensure the backup was successful (200 OK)
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKUP_URL")

echo "HTTP status: $HTTP_STATUS"

# check if file was successfully created
if [ -s "$BACKUP_FILE" ]; then
  echo "backup completed successfully"
else
  echo "backup failed"
fi

echo "creating KG snapshot.."
python obd_ontology/knowledge_snapshot.py --perspective expert >> $KG_SNAPSHOT_FILE
python obd_ontology/knowledge_snapshot.py --perspective diag >> $KG_SNAPSHOT_FILE
