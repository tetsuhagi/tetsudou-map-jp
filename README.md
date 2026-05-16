# 鉄道Now（簡易版）

「鉄道Now」風の、主要特急列車の運行をマップ上で可視化するWebアプリ。
時刻表データは手動でCSV管理。フレームワーク不使用、純粋なHTML/JS/CSSのみ。

## 特徴

- 日本全国を俯瞰できるズームレベル（minZoom: 4）
- Leaflet + OpenStreetMap タイル（無料・APIキー不要）
- OpenStreetMapから取得した実線路ジオメトリで描画・補間（精度 ~75m）
- 時刻表データはCSVで手動管理（スクレイピング無し）

## 起動方法

ES Modulesと`fetch`を使うため、ローカルサーバーが必要です。

```bash
cd ~/Documents/tetsudou-now
python3 -m http.server 8000
```

ブラウザで http://localhost:8000 を開く。

## データ構造

### `data/stations.csv`
駅の座標。
```
station_id,name,lat,lon
TOKYO,東京,35.681236,139.767125
```

### `data/routes.csv`
路線のメタ情報と駅順序。
```
route_id,name,color,display_id,icon,stations
TOKAIDO_SHINKANSEN,東海道新幹線,#0066cc,N,assets/icons/nozomi.png,TOKYO|SHINAGAWA|...
```

### `data/trains.csv`
列車のメタ情報。
```
train_id,name,route_id,direction
NOZOMI_1,のぞみ1号,TOKAIDO_SHINKANSEN,down
```

### `data/schedule.csv`
列車ごとの停車駅と時刻。始発駅は `arrival` を空、終着駅は `departure` を空に。
```
train_id,stop_order,station_id,arrival,departure
NOZOMI_1,1,TOKYO,,06:00
NOZOMI_1,2,SHINAGAWA,06:07,06:08
```

### `data/geometry/<route_id>.json`
国土数値情報（MLIT）から取得した路線ジオメトリ（実線路の高精度ポリライン）。
```json
{
  "polyline": [[35.68, 139.76], ...],
  "station_positions": {"TOKYO": 0, "SHINAGAWA": 159, ...}
}
```
存在しない場合は駅座標を直線で繋いだ簡易版が自動的に使用されます。

## 新しい路線を追加する手順

1. 必要な駅を `stations.csv` に追加
2. `routes.csv` に新しい路線を追加（OSMでの路線名を控えておく）
3. 高精度ジオメトリを生成（国土数値情報からダウンロード・処理）:
   ```bash
   python3 scripts/build_geometry.py <route_id> <MLIT上の路線名> <始発駅ID> <終着駅ID>
   ```
   例:
   ```bash
   python3 scripts/build_geometry.py TOKAIDO_SHINKANSEN 東海道新幹線 TOKYO SHIN_OSAKA
   python3 scripts/build_geometry.py SANYO_SHINKANSEN 山陽新幹線 SHIN_OSAKA HAKATA
   ```
   MLITの路線名は `.cache/N02-23_RailroadSection.geojson` の `N02_003` プロパティで確認できます。
4. 列車を `trains.csv` に追加
5. 時刻表を `schedule.csv` に追加

ブラウザを再読み込みすれば反映されます。

## 今後の拡張アイデア

- サンダーバード、スーパーはくと等の在来線特急を追加
- 列車クリックで詳細時刻表をポップアップ
- 速度や遅延情報を持たせる
