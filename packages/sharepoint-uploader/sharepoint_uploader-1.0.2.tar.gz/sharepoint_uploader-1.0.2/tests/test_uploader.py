from sharepoint_uploader import SharePointUploader

# Initialize client
uploader = SharePointUploader(
    client_id="a03c1cf8-2390-41be-9220-66cb233aa030",
    client_secret="mOP8Q~K4va9yiJ235yIqROZm8SEZez2FB4VByaUN",
    tenant_id="de50c85b-4591-47e7-a359-8b5bf827b744",
    drive_name="Logs",
    site_domain_name="thefruitpeople.sharepoint.com"  # optional
)

# Upload a file
uploader.upload_file(r"C:\Users\RizwanaShaik\The Fruit People Ltd\Projects - General\Projects\66 - SharePoint Uploader Module\requirements.txt", "Logs/Financial/Quarterly")

# Upload a DataFrame
# import pandas as pd
# df = pd.DataFrame({"data": [1, 2, 3]})
# uploader.upload_dataframe_as_csv(df, "quarterly_report.csv", "3 - Test/Financial/Quarterly")