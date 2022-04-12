# marathon-parameter-tuning

parameter tuning environment for heuristics contest.
最小化問題を扱う点に注意.

## 利用方法

1. config.yml を用意する
    * 記載方法は後述
2. `pipenv run python optimizer/optimize.py CONFIG_PATH` を実行する

## 設定可能パラメータ

### 設定パラメータ例

```yaml
dataset_size: 5
number_of_iteration: 100
exec_path: "./main"
parallel_job_size: 1
param_list:
  - name: start_temperature
    type: float
    range_from: 50
    range_to: 10
    scale: log
  - name: end_temperature
    type: float
    range_from: 5
    range_to: 0.1
    scale: log
  - name: opt2_rate
    type: float
    range_from: 0.0
    range_to: 1.0
    scale: linear
  - name: input_data
    type: dataset
    template: "rust/tools/in/{}.txt"
    is_redirect: true
```

### グローバルパラメータ

yaml のグローバルに設定できるパラメータは以下の通りである

| パラメータ名 | 型 | 意味 | 制約 |
| ---- | ---- | ---- | ---- |
| dataset_size | int | 使うデータセットの個数。番号は 0～$dataset_size - 1まで | > 0 |
| exec_path | str | 実行バイナリのパス |  |
| parallel_job_size | int | | > 0 |
| number_of_iteration | int | | > 0 |

### ローカルパラメータ一覧

ローカルパラメータは、実行時引数としてバイナリに渡されるパラメータ一覧を示したもので、yaml の `param_list:` に登録し、この順でソルバに渡される。

パラメータの種類は、以下の通りである。

* `float`
* `int`
* `string`
* `dataset`

#### 共通で設定できるパラメータ

| パラメータ名 | 型 | 意味 | 制約 |
| ---- | ---- | ---- | ---- |
| name | str | パラメータ名 |  |
| type | str | パラメータの種類。上記4種類のいずれか |  |

#### 固有に設定できるパラメータ

`float` の設定項目は以下の通り

| パラメータ名 | 型 | 意味 | 制約 |
| ---- | ---- | ---- | ---- |
| range_from | float | float の区間の開始 |  |
| range_to | float | float の区間の終了 |  |
| scale | enum(log | linear) | 区間の分割方法 |  |


`int` の設定項目は以下の通り

| パラメータ名 | 型 | 意味 | 制約 |
| ---- | ---- | ---- | ---- |
| range_from | int | int の区間の開始 |  |
| range_to | int | int の区間の終了 |  |
| scale | enum(log | linear) | 区間の分割方法 |  |

`string` の設定項目は以下の通り

| パラメータ名 | 型 | 意味 | 制約 |
| ---- | ---- | ---- | ---- |
| value | str | 文字列の値。(バイナリに特有の文字列を渡す必要がある場合を想定) |  |

`dataset` の設定項目は以下の通り

| パラメータ名 | 型 | 意味 | 制約 |
| ---- | ---- | ---- | ---- |
| template | str | データセットの文字列フォーマット。`gnu parallel` でのテンプレートを想定。 |  |
| is_redirect | str | 入力データをリダイレクトで受け取るか否か。ファイルパスをバイナリが受け取るケースを想定。 |  |
