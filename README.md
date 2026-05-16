# 鉄道Now（簡易版）

「鉄道Now」風の、主要特急列車の運行をマップ上で可視化するWebアプリ。
時刻表データは手動でCSV管理。フレームワーク不使用、純粋なHTML/JS/CSSのみ。

## 特徴

- 日本全国を俯瞰できるズームレベル（minZoom: 4）
- Leaflet + OpenStreetMap タイル（無料・APIキー不要）
- 駅間は直線で補間
- 時刻表データはCSVで手動管理（スクレイピング無し）

## 起動方法

ES Modulesと`fetch`を使うため、ローカルサーバーが必要です。

```bash
cd ~/Documents/tetsudou-now
python3 -m http.server 8000
```

ブラウザで http://localhost:8000 を開く。

## データ構造

すべて `data/` 配下のCSV。

### `stations.csv`
駅の座標。
```
station_id,name,lat,lon
TOKYO,東京,35.681236,139.767125
```

### `routes.csv`
路線の駅順序。`stations` 列はパイプ区切り。
```
route_id,name,color,stations
TOKAIDO_SHINKANSEN,東海道新幹線,#0066cc,TOKYO|SHINAGAWA|...
```

### `trains.csv`
列車のメタ情報。`direction` は表示色分けに使用（`down` = 赤、`up` = 青）。
```
train_id,name,route_id,direction
NOZOMI_1,のぞみ1号,TOKAIDO_SHINKANSEN,down
```

### `schedule.csv`
列車ごとの停車駅と時刻。始発駅は `arrival` を空、終着駅は `departure` を空に。
```
train_id,stop_order,station_id,arrival,departure
NOZOMI_1,1,TOKYO,,06:00
NOZOMI_1,2,SHINAGAWA,06:07,06:08
```

## 列車を追加する手順

1. 新しい駅があれば `stations.csv` に追記
2. 新しい路線なら `routes.csv` に1行追加（駅IDをパイプで繋ぐ）
3. 列車を `trains.csv` に追加
4. その列車の時刻表を `schedule.csv` に追記

ブラウザを再読み込みすれば反映されます。

## 今後の拡張アイデア

- サンダーバード、スーパーはくと等の在来線特急を追加
- 列車クリックで詳細時刻表をポップアップ
- 速度や遅延情報を持たせる
- 駅間を実線路polylineで描画（直線ではなく）
