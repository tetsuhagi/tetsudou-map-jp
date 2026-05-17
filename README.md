# 鉄道Now（簡易版）

「鉄道Now」風の、主要特急列車の運行をマップ上で可視化するWebアプリ。
時刻表データは手動でCSV管理。フレームワーク不使用、純粋なHTML/JS/CSSのみ。

## 特徴

- 日本全国を俯瞰できるズームレベル（minZoom: 4）
- Leaflet + OpenStreetMap タイル（無料・APIキー不要）
- 国土数値情報（MLIT）の実線路ジオメトリで描画・補間（精度 ~100m以内）
- 平日/土日祝ダイヤを自動切替
- 時刻表データはCSVで手動管理（スクレイピング無し）

## 起動方法

ES Modulesと`fetch`を使うため、ローカルサーバーが必要です。

```bash
cd ~/Documents/tetsudou-map-jp
python3 -m http.server 8000
```

ブラウザで http://localhost:8000 を開く。

## データ構造

```
data/
├── stations.csv                       # 駅マスタ（全路線共通）
├── routes.csv                         # 路線マスタ（全路線共通）
├── geometry/<route_id>.json           # 路線ジオメトリ（自動生成）
└── timetables/
    ├── TOKAIDO_SHINKANSEN/
    │   ├── trains.csv                 # この路線の列車一覧
    │   ├── weekday.csv                # 平日ダイヤ
    │   └── holiday.csv                # 土日祝ダイヤ（任意）
    ├── SANYO_SHINKANSEN/
    │   └── ...
    └── ...
```

### `data/stations.csv`
全路線で共有する駅マスタ。
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

### `data/timetables/<route_id>/trains.csv`
この路線を走る列車のメタ情報。
```
train_id,name,direction
NOZOMI_1,のぞみ1号,down
```

### `data/timetables/<route_id>/weekday.csv` / `holiday.csv`
列車ごとの停車駅と時刻。始発駅は `arrival` を空、終着駅は `departure` を空に。
土曜・日曜・祝日は `holiday.csv` が使われ、無い場合は `weekday.csv` にフォールバック。
```
train_id,stop_order,station_id,arrival,departure
NOZOMI_1,1,TOKYO,,06:00
NOZOMI_1,2,SHINAGAWA,06:07,06:08
```

### `data/geometry/<route_id>.json`
国土数値情報（MLIT）から自動生成された路線ジオメトリ。
```json
{
  "polyline": [[35.68, 139.76], ...],
  "station_positions": {"TOKYO": 0, "SHINAGAWA": 159, ...}
}
```

## 新しい路線を追加する手順

1. 必要な駅を `data/stations.csv` に追加（MLITで座標確認推奨）
2. `data/routes.csv` に新しい路線を追加（MLITでの路線名を控えておく）
3. 高精度ジオメトリを生成:
   ```bash
   python3 scripts/build_geometry.py <route_id> <MLIT上の路線名> <始発駅ID> <終着駅ID>
   ```
   例:
   ```bash
   python3 scripts/build_geometry.py TOKAIDO_SHINKANSEN 東海道新幹線 TOKYO SHIN_OSAKA
   ```
4. `data/timetables/<route_id>/` ディレクトリを作成
5. `data/timetables/<route_id>/trains.csv` に列車一覧を追加
6. `data/timetables/<route_id>/weekday.csv` に平日ダイヤを追加
7. （任意）`data/timetables/<route_id>/holiday.csv` に土日祝ダイヤを追加

ブラウザを再読み込みすれば反映されます。

## 今後の拡張アイデア

- 在来線特急（サンダーバード、ひだなど）を追加
- 私鉄特急（小田急ロマンスカー、近鉄特急など）を追加
- 列車クリックで詳細時刻表をポップアップ
- 日本の祝日カレンダー対応
