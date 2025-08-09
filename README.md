# Current Capacity: Sentinel2 from Earth-Search (Element84) + NOAA GOES

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Example: list a few Sentinel-2 L2A items from Earth Search
sat search --collections sentinel-2-l2a --limit 3

# OR Example: Search with AOI
sat search --satellite sentinel-2 --product L2A \
  --time 2024-07-01/2024-07-02 \
  --limit 2 \
  --aoi test_aoi_big/aoi.shp \
  --explain

# ----------------------------------------------------------------------------

# Example: download first item (all assets) in July 2024 over a bounding box
sat download --collections sentinel-2-l2a \
  --time 2024-07-01/2024-07-02 \
  --bbox -122.6,37.6,-122.2,37.9 \
  --limit 1

# OR Example:Download filtered by AOI
sat download --satellite sentinel-2 --product L2A \
  --time 2024-07-01/2024-07-02 \
  --limit 1 \
  --aoi test_aoi_big/aoi.shp \
  --assets red,green,blue

# ----------------------------------------------------------------------------

# Example: Generate AOI-cropped Quicklook (usually RGB)
sat quicklook "data/sentinel-2-l2a/S2A_17SNU_20240701_0_L2A" \
  --assets red,green,blue \
  --aoi test_aoi_big/aoi.shp \
  --buffer 0.01


```


AWS Credentials
If you want to download Requester Pays datasets like Landsat C2/L2, 
copy .env.example to .env and fill in your values.

Then run:
```bash
export $(grep -v '^#' .env | xargs)
```
Or use direnv / Docker --env-file. An env.example file exists inside the repo, 
which the code will pick up if you add your information into it.

Some helpful links if you're really new to all this/just for reference:

1. AWS CLI env var setup:
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html

2. Configuring AWS profiles:
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html

3. Requester Pays info:
https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html
