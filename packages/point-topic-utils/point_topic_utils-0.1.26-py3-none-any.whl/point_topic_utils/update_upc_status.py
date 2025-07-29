from datetime import datetime, timezone
from pymongo.results import UpdateResult

from .db.mongodb import MongoDBClient
from .db.snowflake import SnowflakeDB

def update_upc_status_process(
    update_deliverables: bool = True
):
    """
    Queries Snowflake for UPC status, updates MongoDB UpcStatus collection,
    and optionally updates Deliverables collection.
    """
    snowflake_db = None
    mongo_client = None

    try:
        # 1. Connect to Snowflake
        snowflake_db = SnowflakeDB()
        snowflake_db.connect()

        # 2. Query Snowflake for status variables
        snowflake_query = "select * from upc_client._status.upc_status_variables;"
        status_df = snowflake_db.query_to_df(snowflake_query)

        # 3. Connect to MongoDB
        mongo_client = MongoDBClient()
        print("Connected to MongoDB.")

        # 4. Transform Snowflake data and prepare for MongoDB upsert
        upc_status_collection_name = "UpcStatus"
        status_items_for_mongo = []

        if not status_df.empty:
            # Snowflake query returns a single row; iterate through its columns
            # Assuming the first (and only) row contains the relevant data
            snowflake_row = status_df.iloc[0]
            for column_name, value in snowflake_row.items():
                status_items_for_mongo.append({
                    "name": str(column_name), # Each Snowflake column header is a 'name'
                    "value": str(value)       # The cell content is the 'value'
                })
            print(f"Transformed {len(status_items_for_mongo)} items from Snowflake row.")
        else:
            print("Snowflake query returned no data.")

        # Add the special 'lastRefresh' document
        # As per MongoDB example: {"name":"lastRefresh", "varName":"UPC_LAST_REFRESH", "prettyName":"UPC Last Refresh", "value":"ISO_STRING_TIMESTAMP"}
        current_time_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z") # Ensure UTC and Z format
        status_items_for_mongo.append({
            "name": "lastRefresh",
            "value": current_time_iso,
            "varName": "UPC_LAST_REFRESH",
            "prettyName": "UPC Last Refresh"
        })
        print(f"Added 'lastRefresh' item. Total items to process: {len(status_items_for_mongo)}")

        # Upsert items into UpcStatus collection
        if not status_items_for_mongo:
            print("No status items to upsert into MongoDB.")
        else:
            print(f"Upserting {len(status_items_for_mongo)} items into '{upc_status_collection_name}'...")
            for item in status_items_for_mongo:
                mongo_name = item.get("name")
                mongo_value = item.get("value")
                mongo_var_name = item.get("varName")      # Optional
                mongo_pretty_name = item.get("prettyName")  # Optional

                if mongo_name is None:
                    print(f"Skipping item due to missing 'name': {item}")
                    continue

                update_data = {
                    "name": str(mongo_name),
                    "value": str(mongo_value) # Value is always stored as string per requirements
                }
                if mongo_var_name is not None:
                    update_data["varName"] = str(mongo_var_name)
                if mongo_pretty_name is not None:
                    update_data["prettyName"] = str(mongo_pretty_name)
                
                # Removed the generic "last_refresh_time" field from here,
                # as the refresh timestamp is now handled by the 'value' of the 'lastRefresh' document,
                # and the UpcStatus model (name, varName, prettyName, value) does not include last_refresh_time.

                filter_query = {"name": str(mongo_name)}

                result: UpdateResult = mongo_client.upsert_one_in_collection(
                    collection_name=upc_status_collection_name,
                    filter_query=filter_query,
                    update_data=update_data,
                    upsert=True
                )
                if result.upserted_id:
                    print(f"Inserted new UpcStatus: {mongo_name}")
                elif result.modified_count > 0:
                    print(f"Updated UpcStatus: {mongo_name}")
                else:
                    print(f"UpcStatus {mongo_name} already up-to-date or no changes made.")

        print("UPC status upsert process completed.")

        # 5. Optionally update Deliverables to set queryHasChanged: true
        if update_deliverables:
            deliverables_collection_name = "Deliverables"
            print(f"Updating all documents in '{deliverables_collection_name}' to set queryHasChanged=true...")
            update_result = mongo_client.update_many_in_collection(
                collection_name=deliverables_collection_name,
                filter_query={},
                update_data={
                    "queryHasChanged": True,
                    "linkGeneratedAt": None,
                    "linkState": None
                }
            )
            print(f"Matched {update_result.matched_count} documents, modified {update_result.modified_count}.")
            print("Deliverables update process completed.")
        else:
            print("Skipping Deliverables update as requested.")

    except Exception as e:
        print(f"An error occurred during the UPC status update process: {e}")
        # traceback.print_exc() # For more detailed error logging if needed

    finally:
        if snowflake_db:
            snowflake_db.close_connection()
        if mongo_client:
            mongo_client.close()
            print("MongoDB connection closed.")

# Example usage (for testing/demonstration, typically this would be triggered by another script)
# if __name__ == "__main__":
#     # To update both status and deliverables
#     # update_upc_status_process(update_deliverables=True)
#
#     # To update only status
#     # update_upc_status_process(update_deliverables=False)
#     pass 