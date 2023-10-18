Place all views in this directory. When `manage.py` is run with the `--refresh-views` flag, all `.sql` files in this directory will be executed against all databases. 

In order to avoid any errors, make sure your `.sql` file first attempts to drop the view, and *then* creates the view. Example below:

```sql
DROP VIEW IF EXISTS test_view;

CREATE VIEW test_view AS
SELECT * FROM some_table;
```
