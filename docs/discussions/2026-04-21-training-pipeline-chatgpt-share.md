# Пайплайн обучения диффузионки

- Source URL: https://chatgpt.com/share/69e75cfa-ded8-8385-b5c7-c8b64327dbef
- Capture date: 2026-04-21
- Capture format: visible ChatGPT share conversation, turn-by-turn text only.

## Turn 1 - User

Я хочу приступать к дообучению диффузионной модели. Что бы генерировала тень.
Так как это мой проект для портфолио важно грамотно выстроить пайплайн обучения. Логирование, версиыичирование и прочее. По стандартам индустрии 2026.

Какие Фреймворки? Сайты? Сервисы?
С самой моделью и датасетом примерно ясно.
Это будет диффузионка  с расширенным входом. И Лора. Хотя может и контролнет.

## Turn 2 - Assistant

Соберу это как практичный стек под 2026: обучение, трекинг, версии данных/моделей, оркестрация и деплой-эксперименты. Заодно отмечу, где для твоего кейса с тенью лучше LoRA, а где ControlNet/condition-branch.

Уже вырисовывается нормальный индустриальный набор: Diffusers/Accelerate для обучения, DVC или lakeFS для данных, W&B или MLflow для экспериментов и registry. Сейчас доберу оркестрацию, конфиги и CI, чтобы не осталось “дыр” в пайплайне.

Для портфельного CV/DL-проекта в 2026 я бы строил пайплайн не вокруг “самой модной тулзы”, а вокруг воспроизводимости, трассируемости артефактов и быстрого цикла экспериментов. Для твоего кейса это особенно важно: тень — штука визуально тонкая, и без хорошего трекинга легко получить хаос из “вроде стало лучше, но непонятно почему”. В индустрии для этого обычно разделяют: код и CI, конфиги, трекинг экспериментов, версионирование данных/чекпоинтов, оркестрацию запусков и реестр моделей.
MLflow AI Platform
+3
hydra.cc
+3
MLflow AI Platform
+3

Мой главный совет: не делать monolith-ноутбук как центр проекта. Базовый путь — Diffusers + Accelerate для тренировки, Hydra/OmegaConf для конфигов, W&B или MLflow для трекинга, DVC для данных и экспериментов, GitHub Actions для CI. Это очень “читаемый” стек для работодателя: видно, что ты не просто натренировал модель, а умеешь вести ML-проект по-взрослому. Accelerate официально позиционируется как способ запускать один и тот же PyTorch-код в разных distributed-конфигурациях, а Diffusers поддерживает training examples для LoRA, ControlNet, text-to-image и других diffusion-задач. Hydra и OmegaConf дают композицию YAML-конфигов, CLI overrides, типобезопасность и отдельные output-директории на каждый запуск.
hydra.cc
+7
Hugging Face
+7
Hugging Face
+7

По самой модели: для задачи “добавить реалистичную тень объекту на светлом фоне” я бы не ставил LoRA как единственный механизм управления. LoRA хороша как параметр-эффективная адаптация — она быстрее и дешевле, потому что обучает небольшое число добавленных весов, а не всю модель. Но если тебе нужна пространственно контролируемая тень — с правильной геометрией относительно маски объекта, точки контакта и направления света — то одна чистая LoRA может оказаться слишком “стилевой”. ControlNet как раз создан для добавления пространственного conditioning поверх замороженного backbone. Поэтому наиболее разумный дизайн для портфолио: база = diffusion backbone, conditioning branch = mask/depth/light map, adaptation = LoRA для удешевления fine-tune, а не “LoRA вместо всего”.
Hugging Face
+3
Hugging Face
+3
Hugging Face
+3

Если совсем приземлённо, я бы рассматривал 3 варианта архитектуры:

LoRA-only — как baseline: быстро, дёшево, полезно для первой проверки идеи.
Hugging Face
+1

Extended input / custom conditioning — если ты уже расширяешь вход маской, бинарной картой контакта, направлением света, глубиной или shadow prior. Это ближе к исследовательскому CV-проекту и лучше смотрится в портфолио.

ControlNet / Control-LoRA hybrid — если хочешь устойчивый spatial control. Для задачи тени это часто самый “продуктовый” путь, потому что можно явно управлять структурой результата, а не надеяться, что модель “сама поймёт”. Официальные Diffusers-пайплайны и training examples это направление покрывают.
Hugging Face
+2
Hugging Face
+2

Из трекинга экспериментов я бы выбирал так. W&B — лучший выбор, если хочешь красивую демонстрацию проекта, удобные графики, медиа-логи, таблицы с изображениями, lineage артефактов и хорошую “витрину” для портфолио. W&B официально поддерживает логирование метрик, гиперпараметров, системных метрик и model/data artifacts, а также lineage-графы артефактов. Для diffusion/CV это особенно удобно, потому что можно логировать одинаковый фиксированный eval-set картинок на каждом чекпоинте и буквально смотреть, как меняется тень.
docs.wandb.ai
+3
docs.wandb.ai
+3
docs.wandb.ai
+3

MLflow я бы брал, если хочешь более “enterprise-neutral” и self-hosted стек без сильной привязки к одному SaaS. У MLflow есть Tracking и Model Registry: параметры, метрики, артефакты, версии моделей, алиасы и lineage от run к model version. Для работодателя MLflow тоже выглядит очень солидно, особенно если покажешь отдельный tracking server и registry. Но по удобству визуального анализа изображений и быстрых qualitative review W&B обычно приятнее.
MLflow AI Platform
+3
MLflow AI Platform
+3
MLflow AI Platform
+3

ClearML — нормальный вариант, если хочется auto-capture запуска и удалённый execution с минимальным количеством ручной обвязки. У него Task — центральная сущность эксперимента, и он умеет автоматически собирать код/конфиг/outputs. Но если выбирать один стек под сильное портфолио в diffusion/CV, я бы всё же ставил W&B > MLflow > ClearML.
ClearML
+2
docs.wandb.ai
+2

Для данных и чекпоинтов мой выбор для такого проекта — DVC. Он прямо позиционируется как Git-like version control для data science / ML, а в конце 2025–2026 у него остаётся сильная роль именно для индивидуальных исследователей и маленьких команд, в то время как lakeFS больше уходит в enterprise-scale data lakes. Для твоего кейса DVC хорош тем, что можно версионировать: исходные изображения, маски, парные таргеты с тенями, split-файлы, preprocess outputs, eval sets и ссылки на чекпоинты.
DVC
+2
DVC
+2

Правильная схема здесь такая: Git хранит код и конфиги, DVC хранит большие данные и производные артефакты, experiment tracker хранит метрики/медиа, model registry хранит “approved” модели. Не пытайся одной системой закрыть всё. Это как раз тот признак зрелости пайплайна, который любят в индустрии.
DVC
+2
docs.wandb.ai
+2

По конфигам я бы жёстко использовал Hydra + OmegaConf. Причина простая: diffusion-проекты быстро обрастают десятками параметров — база модели, rank LoRA, learning rates для разных блоков, scheduler, guidance settings на eval, тип conditioning, аугментации, лоссы, веса регуляризаторов, пути к датасетам, seed, mixed precision, checkpoint cadence. Hydra даёт композицию конфигов и CLI-overrides, а OmegaConf — удобные YAML-конфиги и structured configs с runtime type safety. Плюс Hydra автоматически создаёт отдельный output-dir для каждого запуска и сохраняет туда конфиг и overrides, что очень полезно для воспроизводимости.
hydra.cc
+3
hydra.cc
+3
omegaconf.readthedocs.io
+3

Для управления окружением в 2026 я бы скорее выбрал uv, а не Poetry, если нет особых причин иначе. uv сейчас официально позиционируется как очень быстрый Python package/project manager, умеет работать с pyproject.toml, lock-файлом и даже устанавливать Python-версии. Poetry всё ещё нормален и зрел, но для нового проекта uv сейчас выглядит более современно и практично.
Poetry
+3
Astral Docs
+3
Astral Docs
+3

Для качества кода и CI я бы ставил минимальный, но строгий набор: Ruff + mypy + pytest + pre-commit + GitHub Actions. Ruff объединяет linter и formatter, mypy даёт статическую проверку типов, pytest — тесты, pre-commit — автоматические хуки перед коммитом, GitHub Actions — CI/CD. GitHub официально описывает Actions как CI/CD платформу, а pre-commit, Ruff и mypy имеют стабильную официальную документацию и стандартно используются в Python-проектах.
GitHub Docs
+6
Astral Docs
+6
Astral Docs
+6

Что тестировать в таком ML-проекте:

загрузчик датасета и парность (input, target, mask, metadata);

корректность preprocess/augmentations;

shape/contracts для всех тензоров;

deterministic smoke-train на 1–2 батчах;

inference regression test на mini eval-set;

вычисление метрик;

сериализацию чекпоинта и загрузку обратно.
Это не заменяет визуальную оценку, но сильно сокращает “тихие” поломки пайплайна. pytest для этого вполне достаточно.
Документация pytest
+1

Для оркестрации запусков я бы не брал тяжёлый MLOps-комбайн без нужды. Если ты один и проект исследовательский, то часто хватает Hydra multirun + W&B sweeps или Ray Tune, если нужен нормальный HPO. Ray Tune официально позиционируется как библиотека для execution и hyperparameter tuning “at any scale”. Prefect имеет смысл только если у тебя появится отдельный production-like pipeline: сбор датасета, nightly preprocess, регулярные eval-job’ы, автообновление leaderboards и так далее. Для текущего этапа он, вероятно, избыточен.
docs.prefect.io
+3
docs.ray.io
+3
docs.ray.io
+3

Самая важная часть именно для diffusion с тенью — evaluation pipeline. В логирование нужно включить не только loss curves, но и:

фиксированный набор validation сцен;

одинаковые seeds;

side-by-side панели: input / GT / pred / alpha / mask / shadow-only diff;

несколько категорий объектов: обувь, бутылки, техника, мягкие предметы;

разбиение по “сложности тени”: контактная, мягкая рассеянная, длинная направленная;

метрики по shadow mask / shadow region отдельно от фона и объекта.
В W&B это удобно оформляется через media logging, tables и plots; в MLflow тоже можно, но обычно менее удобно для визуального перебора.
docs.wandb.ai
+2
docs.wandb.ai
+2

Для registry моделей я бы делал не просто “папку checkpoints”, а явные стадии. Например:

candidate

validated

demo

archive
У MLflow Model Registry есть версии, алиасы, теги и lineage; у W&B тоже есть model/artifact workflows. Это позволит показать, что у тебя есть не только обучение, но и процесс принятия модели.
docs.wandb.ai
+3
MLflow AI Platform
+3
MLflow AI Platform
+3

Практический стек, который я бы тебе рекомендовал как основной:

Вариант A — лучший баланс для портфолио

Training: PyTorch + Diffusers + Accelerate

Configs: Hydra + OmegaConf

Tracking: W&B

Data versioning: DVC

Env/deps: uv

Quality/CI: Ruff + mypy + pytest + pre-commit + GitHub Actions
Это даст красивый, современный и очень “читаемый” проект.
GitHub Docs
+7
Hugging Face
+7
Hugging Face
+7

Вариант B — более self-hosted / enterprise-neutral

Training: PyTorch + Diffusers + Accelerate

Configs: Hydra + OmegaConf

Tracking + Registry: MLflow

Data versioning: DVC

CI: GitHub Actions

HPO: Ray Tune по необходимости
Это выглядит чуть суше, но хорошо продаётся как “production-minded ML workflow”.
GitHub Docs
+5
Hugging Face
+5
MLflow AI Platform
+5

Что я бы не делал:
не начинал бы с full fine-tune всей диффузионки без baseline на LoRA; не хранил бы датасет в Git LFS как основную систему версий; не делал бы только ноутбуки без CLI train/eval; не оставлял бы qualitative evaluation “в голове”; не смешивал бы train/eval/demo скрипты в один файл. Эти вещи очень быстро портят воспроизводимость. Основание тут не в одном конкретном сервисе, а в том, как официальные инструменты разделяют tracking, config composition, artifact versioning и CI.
GitHub Docs
+3
Hugging Face
+3
DVC
+3

Если смотреть именно на твою задачу, я бы предложил такой порядок работ:
сначала сделать baseline LoRA на фиксированном датасете и полном пайплайне трекинга; потом добавить расширенный conditioning input; после этого сравнить с ControlNet-подходом на одном и том же eval protocol. Для портфолио это очень сильная история: “я не просто натренировал модель, я сравнил 3 класса решений в воспроизводимой среде”.
DVC
+4
Hugging Face
+4
Hugging Face
+4

Если хочешь, следующим сообщением я могу собрать тебе конкретную структуру репозитория под этот проект: папки, YAML-конфиги, naming conventions для runs, схему DVC stages и что именно логировать в W&B на каждом train/eval шаге.

## Turn 3 - User

Все предложения мне нравятся. Вариант а.

По поводу dvc только у меня раньше были проблемы. Пару лет назад я пробовал версивифировать датасет и там все проваливалось в какой-то ад, оно кусу времени обрабатывало эти тысячи файлов и получалось как-то неповоротливо. Особенно с учетом ненаглядности интерфейса dvc. Сейчас что-то изменилось? Как все выстроить так что бы оно помогало и не стращать.

В реальности датасеты будут храниться на локальном компе и максимум использоваться из локальной сети.
Хотя для понтов можно подключить s3 Яндекс клауда

## Turn 4 - Assistant

Проверю, что у DVC реально изменилось и какие сейчас есть более лёгкие схемы для локального NAS/домашней сети. Заодно отберу вариант без “ада с тысячами файлов”, чтобы стек остался индустриальным, но не душил в быту.

Главный вывод уже есть: DVC не “починился магически”, но у него есть режимы, где он не должен быть тормозным. Узкое место обычно не сам Git-метафайл, а схема “тащим в рабочую папку десятки тысяч мелких файлов копированием”. Сейчас добираю, как это обойти правильно именно для локального хранилища.

Да, твой прошлый опыт с DVC очень похож на типичный: если пытаться “по-честному” завернуть в DVC огромную россыпь мелких файлов и работать с ней как с обычной папкой проекта, получается тяжело и неочевидно. Сейчас у DVC есть полезные режимы и сценарии для локального/сетевого хранения, но он не превратился в магически простой GUI-инструмент. Это всё ещё в первую очередь CLI-система с кэшем, remotes и .dvc-метафайлами. При этом официальный стек DVC по-прежнему поддерживает local filesystem remotes, shared cache и работу с внешними данными, так что для домашнего ПК/NAS его можно настроить без S3 и без лишней боли.
Data Version Control · DVC
+3
Data Version Control · DVC
+3
Data Version Control · DVC
+3

Мой честный вывод: для твоего проекта DVC имеет смысл, но в “облегчённой” роли. Не как тотальная система для каждого сырого файла датасета, а как средство версионировать срезы датасета, манифесты, split’ы, preprocess outputs, чекпоинты и eval-наборы. Это будет выглядеть индустриально и при этом не станет мучением.

Что реально изменилось и что помогает сейчас:

Во-первых, DVC официально продвигает сценарий shared cache — один общий кэш рядом с данными, в сети или на внешнем диске. В документации прямо сказано, что общий DVC cache может стоять в “near location” вроде сети или external drive, дедуплицировать файлы между проектами и уменьшать лишние передачи данных. Это как раз твой случай: локальный комп + локальная сеть.
Data Version Control · DVC
+1

Во-вторых, у DVC есть несколько типов линковки файлов из кэша в workspace. Официально DVC пишет, что reflink — лучший вариант, а hardlink тоже эффективен; это как раз способ уйти от тяжёлого копирования данных туда-сюда. Если filesystem поддерживает reflink/hardlink, работа становится заметно приятнее, чем в схеме “всё копируем физически”. При этом DVC отдельно предупреждает, что hardlink/symlink делают файлы read-only linked to cache, и для ручного редактирования может понадобиться dvc unprotect.
Data Version Control · DVC
+1

В-третьих, сейчас лучше использовать не только dvc add, но и сценарии с external data / dvc import-url. Документация DVC прямо говорит, что можно трекать данные, которые живут вне локального проекта, и при этом выбирать, скачивать их или нет, а также пушить ли копии в remote. import-url поддерживает и /local/path, то есть источник может быть просто внешней директорией на локальном диске или в сети. Для тебя это важно: датасет может жить вне репозитория, а проект будет хранить только указатель и версию.
Data Version Control · DVC
+2
Data Version Control · DVC
+2

Поэтому я бы строил так:

1. Сырой датасет не класть внутрь репозитория проекта.
Пусть он живёт отдельно, например на диске/NAS:
/data/shadowgen/raw/...

2. В Git-репозитории хранить только:

код;

конфиги;

манифесты и split’ы;

.dvc-файлы;

маленький demo/eval subset;

metadata по версиям датасета.

3. DVC использовать для:

data/interim — результаты preprocess;

data/processed — финальные train/val/test срезы;

artifacts/checkpoints;

artifacts/samples;

artifacts/eval_reports.

Это даёт “индустриальный” вид без попытки заставить DVC быть файловым менеджером для всего мира.

Самый здоровый режим для тебя — не версионировать каждый микросдвиг сырого датасета, а работать версиями уровня:

raw_v1

raw_v2_cleaned

processed_v1_512px

processed_v2_contactshadow

evalset_v1_fixed

То есть мыслить снапшотами набора, а не бесконечным ручным редактированием россыпи файлов. Это уже скорее рекомендация по инженерной практике, но именно она спасает от ощущения “DVC — ад”.

Для локальной инфраструктуры я бы выбрал такую схему:

GitHub — код и CI.

DVC local remote — папка на локальном диске или сетевой шаре.

DVC shared cache — отдельная общая папка рядом с данными.

W&B — эксперименты, картинки, метрики.

Без S3 на старте.

Это полностью соответствует официальной модели DVC: remotes могут быть не только S3, но и local file systems, а shared cache специально описан как способ уменьшать дублирование и переносы.
Data Version Control · DVC
+2
Data Version Control · DVC
+2

Практически я бы делал так:

Bash
# репозиторий
shadowgen/
  configs/
  src/
  scripts/
  data/
    manifests/
    splits/
    sample_eval/
  artifacts/
  dvc.yaml

А сами большие данные — вне репо:

Bash
/mnt/ml-data/shadowgen-raw/
/mnt/ml-cache/dvc-cache/
/mnt/ml-remote/dvc-remote/

И затем:

cache.dir указываешь на общий кэш;

remote делаешь локальной директорией;

в проекте трекаешь уже версии processed data и artifacts.
Официально DVC поддерживает и настройку shared cache, и local remote storage.
Data Version Control · DVC
+2
Data Version Control · DVC
+2

Мой совет по “без страданий” такой:

Не использовать DVC для активного ручного редактирования папки с тысячами raw-файлов.
Используй его после этапа сборки версии датасета. То есть:

ты локально собрал/почистил датасет обычными скриптами;

сгенерировал manifest CSV/JSONL;

заморозил версию;

только потом зарегистрировал её в DVC.

Так DVC становится системой фиксации версий, а не интерактивной рабочей средой для копания в файлах. Именно в такой роли он обычно и полезен.

Отдельно про “понты с S3 Яндекс Клауда”. Это можно сделать, но я бы не делал S3 основой. Сделай локальный remote основным, а S3 — вторичным backup/demo-слоем. DVC официально поддерживает S3 remotes, так что при желании потом можно добавить Яндекс Object Storage как удалённую копию. Но для одного исследовательского проекта с локальным хранением это больше nice-to-have, чем core necessity.
Data Version Control · DVC
+1

Про lakeFS: я бы не советовал его тебе вместо DVC. Официальная документация lakeFS завязана на object store architecture; у них есть local storage adapter, но он описывается как вариант для non-production usages. Для локального индивидуального DL/CV-проекта это уже выглядит как лишняя инфраструктура.
docs.lakefs.io
+1

Итого мой вердикт такой:

DVC стоит брать, если

ты используешь его ограниченно и осмысленно;

большие raw-данные живут вне репо;

версии фиксируются снапшотами;

есть shared cache;

по возможности используешь reflink/hardlink вместо копий.
Data Version Control · DVC
+2
Data Version Control · DVC
+2

DVC не стоит делать центром всей жизни, если

ты постоянно руками меняешь тысячи файлов;

хочешь наглядный GUI вместо CLI;

ожидаешь, что он будет “как Dropbox для датасета”.

В твоём случае я бы выбрал такой компромисс:

Минимально болезненный стек

Git — код

W&B — эксперименты и визуалки

DVC — только версии processed data, checkpoints, eval assets

raw dataset — просто на локальном диске/NAS

manifests/splits — в Git

local DVC remote — на NAS или соседнем диске

S3 Яндекса — потом, как optional backup/demo

Это и выглядит по-индустриальному, и не превращает жизнь в ад.

Дальше я могу собрать тебе конкретную схему папок + dvc.yaml + набор команд dvc config/cache/remote/add именно под такой “щадящий” режим.

## Turn 5 - User

реапозиторий с сервисом у меня называется  ShadowGen-ML-service
как назвать репозиторий где будет обучение?

и распиши подробно структуру проекта, включая файлы с инструкциями агенту open ai codex который будет уже вести этот проект

## Turn 6 - Assistant

Сейчас подберу не просто красивое имя, а схему, которая будет нормально смотреться рядом с ShadowGen-ML-service и не сломается, когда появятся датасеты, эксперименты и отдельный inference/demo. Заодно проверю, как актуально оформлять инструкции для Codex через официальные материалы OpenAI.

Проверил официальные материалы OpenAI: для Codex сейчас действительно правильная точка входа — AGENTS.md, а проектные настройки можно класть в .codex/config.toml. Ещё важный нюанс: OpenAI рекомендует держать инструкции короткими, практичными и связанными с реальными командами/тестами, а не писать огромный “манифест”.
OpenAI разработчики
+2
OpenAI разработчики
+2

Я бы назвал репозиторий для обучения так:

ShadowGen-ML-training

Это лучший вариант рядом с ShadowGen-ML-service, потому что сразу видно разделение ролей:

...-service — inference / API / Telegram / продовый сервис

...-training — датасеты, эксперименты, обучение, eval, чекпоинты

Он читается лучше, чем tr:contentReference[oaicite:0]{index=0}с, а всю исследовательскую и MLOps-обвязку. И он лучше, чем research`, потому что у тебя там будет не только исследование, но и вполне инженерный пайплайн.

Ещё хорошие варианты, если хочешь чуть другой акцент:

ShadowGen-ML-lab — более “R&D/portfolio” стиль

ShadowGen-ML-pipeline — акцент на воспроизводимом ML-пайплайне

ShadowGen-ML-train — короче, но менее солидно звучит

ShadowGen-shadow-training — если захочешь в названии подчеркнуть узкую задачу

Но основной мой выбор всё равно: ShadowGen-ML-training.

Как я бы разделил репозитории

У тебя получится хорошая архитектура из двух реп:

1) ShadowGen-ML-service

Тут живёт:

inference pipeline

API / Telegram bot integration

postprocessing

упаковка модели для сервиса

runtime-конфиги

мониторинг inference

2) ShadowGen-ML-training

Тут живёт:

подготовка датасета

manifests / splits

preprocess

train

eval

ablations

экспорт артефактов в service repo

experiment tracking

DVC stages

W&B integration

Это очень хорошее разделение для портфолио: сразу видно, что ты понимаешь разницу между training system и serving system.

Рекомендуемая структура ShadowGen-ML-training

Ниже дам структуру не “учебную”, а такую, которую реально можно вести через Codex и не развалить через месяц.

ShadowGen-ML-training/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .gitattributes
├─ pyproject.toml
├─ uv.lock
├─ Makefile
├─ AGENTS.md
├─ dvc.yaml
├─ dvc.lock
├─ .dvc/
│  ├─ config
│  ├─ .gitignore
│  └─ tmp/
├─ .codex/
│  ├─ config.toml
│  └─ prompts/
│     ├─ train-task.md
│     ├─ eval-task.md
│     └─ refactor-task.md
├─ .github/
│  ├─ workflows/
│  │  ├─ ci.yml
│  │  ├─ lint.yml
│  │  ├─ smoke-train.yml
│  │  └─ docs.yml
│  ├─ ISSUE_TEMPLATE/
│  │  ├─ bug_report.md
│  │  ├─ experiment.md
│  │  └─ feature_request.md
│  └─ pull_request_template.md
├─ docs/
│  ├─ architecture.md
│  ├─ dataset.md
│  ├─ experiments.md
│  ├─ training.md
│  ├─ evaluation.md
│  ├─ deployment-handoff.md
│  ├─ decisions/
│  │  ├─ 0001-repo-structure.md
│  │  ├─ 0002-tracking-stack.md
│  │  ├─ 0003-dataset-versioning.md
│  │  └─ 0004-conditioning-architecture.md
│  └─ runbooks/
│     ├─ local-setup.md
│     ├─ add-dataset-version.md
│     ├─ run-training.md
│     ├─ run-eval.md
│     └─ export-model-to-service.md
├─ configs/
│  ├─ config.yaml
│  ├─ paths/
│  │  ├─ local.yaml
│  │  ├─ workstation.yaml
│  │  └─ lan_storage.yaml
│  ├─ data/
│  │  ├─ base.yaml
│  │  ├─ shadow_pair_v1.yaml
│  │  ├─ shadow_pair_v2.yaml
│  │  └─ eval_fixed_v1.yaml
│  ├─ model/
│  │  ├─ lora.yaml
│  │  ├─ controlnet.yaml
│  │  ├─ extended_input_unet.yaml
│  │  └─ baseline.yaml
│  ├─ train/
│  │  ├─ base.yaml
│  │  ├─ debug.yaml
│  │  ├─ single_gpu.yaml
│  │  └─ long_run.yaml
│  ├─ eval/
│  │  ├─ base.yaml
│  │  ├─ visual.yaml
│  │  └─ benchmark.yaml
│  ├─ tracker/
│  │  ├─ wandb.yaml
│  │  └─ offline.yaml
│  ├─ dvc/
│  │  └─ base.yaml
│  └─ experiment/
│     ├─ baseline_lora.yaml
│     ├─ ext_input_v1.yaml
│     └─ controlnet_v1.yaml
├─ src/
│  └─ shadowgen_training/
│     ├─ __init__.py
│     ├─ cli/
│     │  ├─ __init__.py
│     │  ├─ train.py
│     │  ├─ eval.py
│     │  ├─ predict.py
│     │  ├─ preprocess.py
│     │  ├─ export.py
│     │  └─ doctor.py
│     ├─ data/
│     │  ├─ __init__.py
│     │  ├─ schema.py
│     │  ├─ dataset.py
│     │  ├─ datamodule.py
│     │  ├─ transforms.py
│     │  ├─ collate.py
│     │  ├─ manifests.py
│     │  ├─ splits.py
│     │  ├─ quality_checks.py
│     │  └─ io.py
│     ├─ models/
│     │  ├─ __init__.py
│     │  ├─ registry.py
│     │  ├─ base.py
│     │  ├─ lora_adapter.py
│     │  ├─ controlnet_adapter.py
│     │  ├─ extended_input_unet.py
│     │  ├─ losses.py
│     │  ├─ schedulers.py
│     │  └─ exporters.py
│     ├─ training/
│     │  ├─ __init__.py
│     │  ├─ engine.py
│     │  ├─ loop.py
│     │  ├─ callbacks.py
│     │  ├─ checkpointing.py
│     │  ├─ ema.py
│     │  ├─ optimization.py
│     │  ├─ reproducibility.py
│     │  └─ accelerate_utils.py
│     ├─ evaluation/
│     │  ├─ __init__.py
│     │  ├─ metrics.py
│     │  ├─ visual_bench.py
│     │  ├─ shadow_region_metrics.py
│     │  ├─ contact_shadow_metrics.py
│     │  ├─ reports.py
│     │  └─ leaderboard.py
│     ├─ inference/
│     │  ├─ __init__.py
│     │  ├─ pipeline.py
│     │  ├─ postprocess.py
│     │  └─ export_contract.py
│     ├─ tracking/
│     │  ├─ __init__.py
│     │  ├─ wandb_logger.py
│     │  ├─ run_context.py
│     │  ├─ artifact_naming.py
│     │  └─ system_info.py
│     ├─ utils/
│     │  ├─ __init__.py
│     │  ├─ paths.py
│     │  ├─ logging.py
│     │  ├─ image_ops.py
│     │  ├─ masks.py
│     │  ├─ hashes.py
│     │  ├─ seed.py
│     │  └─ typing.py
│     └─ version.py
├─ scripts/
│  ├─ setup_local.sh
│  ├─ setup_lan_remote.sh
│  ├─ prepare_dataset.py
│  ├─ build_manifest.py
│  ├─ freeze_dataset_version.py
│  ├─ run_smoke_train.sh
│  ├─ run_baseline_lora.sh
│  ├─ run_eval_fixed.sh
│  ├─ export_best_to_service.py
│  └─ sync_service_artifacts.sh
├─ data/
│  ├─ README.md
│  ├─ manifests/
│  │  ├─ train_v1.parquet
│  │  ├─ val_v1.parquet
│  │  └─ test_v1.parquet
│  ├─ splits/
│  │  ├─ split_v1.json
│  │  └─ split_v2.json
│  ├─ sample_eval/
│  │  ├─ inputs/
│  │  ├─ targets/
│  │  └─ metadata.json
│  └─ external/
│     └─ .gitkeep
├─ artifacts/
│  ├─ .gitkeep
│  ├─ reports/
│  ├─ visualizations/
│  └─ exported/
├─ tests/
│  ├─ conftest.py
│  ├─ test_configs.py
│  ├─ test_dataset.py
│  ├─ test_transforms.py
│  ├─ test_model_contracts.py
│  ├─ test_train_smoke.py
│  ├─ test_eval_smoke.py
│  └─ test_export_contract.py
└─ notebooks/
   ├─ 00_dataset_exploration.ipynb
   ├─ 01_shadow_analysis.ipynb
   └─ 99_scratchpad.ipynb
Что где лежит и зачем
Корень репозитория
README.md

Главный entry point. Должен отвечать на 5 вопросов:

что это за repo

как установить

как запустить smoke-train

как запустить eval

как экспортировать модель в service repo

pyproject.toml

Единая точка для:

зависимости

Ruff

mypy

pytest

entry points CLI

Makefile

Чтобы и ты, и Codex запускали стандартные команды одинаково:

Makefile
install:
	uv sync

lint:
	ruff check .
	ruff format --check .
	mypy src

test:
	pytest -q

test-smoke:
	pytest -q tests/test_train_smoke.py tests/test_eval_smoke.py

train-debug:
	python -m shadowgen_training.cli.train experiment=baseline_lora train=debug

train:
	python -m shadowgen_training.cli.train experiment=baseline_lora train=single_gpu

eval:
	python -m shadowgen_training.cli.eval eval=visual

doctor:
	python -m shadowgen_training.cli.doctor

Это очень важно для Codex: OpenAI прямо рекомендует давать агенту ясные инструкции, какие команды запускать, как тестировать и как следовать практикам репозитория. AGENTS.md для этого и предназначен.
OpenAI
+1
docs/

Это не “для красоты”. Это твой реальный способ удерживать проект в порядке.

docs/architecture.md

Описывает:

какие репозитории есть

как training repo связан с service repo

где граница между обучением и инференсом

какие артефакты публикуются наружу

docs/dataset.md

Очень важный файл. Там нужно описать:

формат примера

где живут raw данные

как строится manifest

какие поля обязательны

как формируется split

какие версии датасета существуют

docs/experiments.md

Реестр экспериментов:

baseline LoRA

extended input

ControlNet

что считается успешным

какие метрики важнее

docs/deployment-handoff.md

Контракт с ShadowGen-ML-service:

какой файл модели экспортируется

какие входы ожидаются

какие preprocessing/postprocessing assumptions есть

какие ограничения у inference

docs/decisions/*.md

Это mini-ADR. Очень хорошая индустриальная штука.
Например:

почему выбрали W&B, а не MLflow

почему DVC только для processed data

почему baseline = LoRA, а не full fine-tune

Папка configs/

Тут весь проект должен жить через Hydra-конфиги.

configs/config.yaml

Главный composition config.

Пример:

YAML
defaults:
  - paths: local
  - data: shadow_pair_v1
  - model: lora
  - train: single_gpu
  - eval: base
  - tracker: wandb
  - dvc: base
  - _self_

project:
  name: shadowgen-ml-training
  task: object_shadow_generation
configs/paths/

Разные окружения:

local.yaml — локальная машина

workstation.yaml — если потом появится отдельный ПК

lan_storage.yaml — если raw/processed лежат в локальной сети

configs/data/

Описывает конкретные версии наборов:

где manifest

размер изображения

наличие depth/light metadata

какие колонки есть

configs/model/

Три главные ветки:

lora.yaml

controlnet.yaml

extended_input_unet.yaml

configs/experiment/

Это уже готовые сценарии:

baseline_lora.yaml

ext_input_v1.yaml

controlnet_v1.yaml

Именно их ты будешь запускать чаще всего.

Папка src/shadowgen_training/
cli/

Все команды должны вызываться отсюда:

train.py

eval.py

preprocess.py

predict.py

export.py

doctor.py

Почему нужен doctor.py

Очень полезно и для тебя, и для Codex.
Он проверяет:

виден ли GPU

доступны ли пути

существует ли manifest

включён ли W&B

доступен ли DVC cache/remote

совпадают ли версии зависимостей

data/

Тут не только Dataset, но и вся дата-инженерия.

schema.py

Описывает контракт примера:

input_image_path

target_image_path

object_mask_path

shadow_mask_path

light_dir

sample_id

split

object_category

manifests.py

Генерация parquet/jsonl manifest.

quality_checks.py

Проверки датасета:

есть ли файлы

не битые ли изображения

совпадают ли размеры

не пустые ли маски

нет ли утечек между split’ами

Это очень хороший кусок для портфолио.

models/

Слой адаптеров над Diffusers / custom modules.

registry.py

Чтобы можно было сказать:

model.name=lora

model.name=controlnet

model.name=extended_input_unet

И всё собиралось через единый factory.

exporters.py

Экспорт в формат, который поймёт service repo.

training/

Сюда вынести всё, что касается train loop.

engine.py

Оркестрация одного запуска.

checkpointing.py

Единая схема нейминга:

last

best_visual

best_shadow_iou

best_contact_shadow

reproducibility.py

Фиксация:

seed

torch deterministic flags

env snapshot

git commit hash

config snapshot

evaluation/

Это отдельный полноценный модуль.

metrics.py

Общие метрики.

shadow_region_metrics.py

Метрики только по области тени.

contact_shadow_metrics.py

Отдельные метрики на контактную тень.

visual_bench.py

Генерация сравнительных панелей:

input

GT

pred

mask

diff

reports.py

Сохраняет markdown/html/json summary.

tracking/

Вынести логирование отдельно — очень правильный шаг.

wandb_logger.py

Логика W&B в одном месте, а не размазана по train loop.

artifact_naming.py

Единая схема имён для run/artifacts:

dataset-shadow-pair-v1

model-baseline-lora-r16

eval-fixed-v1

Папка scripts/

Только тонкие служебные команды, которые часто нужны человеку или агенту.

Особенно полезны:

build_manifest.py

freeze_dataset_version.py

export_best_to_service.py

Папка data/ внутри repo

Только маленькие и воспроизводимые вещи:

manifests

splits

fixed eval subset

metadata

Сырые большие изображения сюда не класть.

Папка artifacts/

Локальные результаты:

отчёты

панели визуализации

экспорт моделей

Обычно эта папка в .gitignore, кроме специально выбранных маленьких файлов.

Папка tests/

Минимальный обязательный набор:

test_configs.py — Hydra-конфиги собираются без ошибок

test_dataset.py — dataset возвращает нужный контракт

test_model_contracts.py — формы тензоров и каналы

test_train_smoke.py — 1–2 batch train проходит

test_eval_smoke.py — eval не падает

test_export_contract.py — экспорт совместим с service repo

Что добавить специально для Codex

OpenAI официально пишет, что Codex читает AGENTS.md перед началом работы, а проектные настройки можно задавать через .codex/config.toml; также они советуют добиваться консистентности через конфигурацию и держать инструкции прикладными.
OpenAI разработчики
+2
OpenAI разработчики
+2
й AGENTS.md

Это главный файл. Он должен быть коротким, рабочим и очень конкретным.

Вот хороший стартовый вариант.

Markdown
# AGENTS.md

## Purpose
This repository contains the training, evaluation, dataset preparation, and model export pipeline for ShadowGen.
The goal is to train diffusion-based models that generate realistic object shadows on light backgrounds.

## Scope
Codex may:
- modify Python source under `src/`
- update Hydra configs under `configs/`
- add or update tests under `tests/`
- update docs under `docs/`
- add small helper scripts under `scripts/`

Codex must not:
- commit generated checkpoints
- add raw datasets into the repository
- rewrite repository structure without strong justification
- introduce heavy dependencies without updating docs and tests

## Ground rules
- Keep changes minimal and local.
- Prefer fixing root causes over patching symptoms.
- Preserve reproducibility.
- Do not hardcode machine-specific absolute paths in tracked files.
- Prefer configuration over magic constants.
- Keep training, evaluation, and export concerns separated.

## Environment
- Python project managed with `uv`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy src`
- Tests: `pytest -q`
- Smoke train: `pytest -q tests/test_train_smoke.py`
- Main CLI:
  - `python -m shadowgen_training.cli.train`
  - `python -m shadowgen_training.cli.eval`
  - `python -m shadowgen_training.cli.preprocess`
  - `python -m shadowgen_training.cli.export`

## Before making changes
Codex should:
1. read `README.md`
2. read relevant files under `docs/`
3. inspect existing configs under `configs/`
4. avoid duplicating existing abstractions

## Coding conventions
- Use type hints on new public functions.
- Keep functions small and composable.
- Put filesystem logic in `utils/paths.py` or dedicated modules.
- Put experiment logging code in `tracking/`, not inside model code unless required.
- Avoid large classes when a small functional module is enough.
- Prefer explicit dataclasses or typed config structures for complex inputs.

## Training conventions
- Every trainable experiment must have:
  - a named Hydra config
  - a smoke-test path
  - W&B logging hooks
  - deterministic seed setup
- Checkpoints must include enough metadata to reproduce the run.

## Evaluation conventions
- Preserve the fixed evaluation subset.
- Do not change metrics silently.
- If metrics change, update docs and tests.
- Log qualitative panels for any model behavior change affecting shadows.

## Data conventions
- Raw datasets live outside Git.
- Repository-tracked data should be limited to manifests, splits, metadata, and tiny sample assets.
- DVC is used for processed datasets and selected artifacts, not for ad hoc raw data dumping.

## Export conventions
- Exported artifacts must match the contract documented in `docs/deployment-handoff.md`.
- If export format changes, update both docs and tests.

## When unsure
Prefer adding a short doc note in `docs/` and a focused test rather than making a broad speculative refactor.
2) Дополнительные AGENTS.md по подпапкам

OpenAI пишет, что инструкции можно наслаивать и переопределять по области проекта. Это полезно, когда репозиторий большой.
OpenAI разработчики
+1
ещё 3 локальных файла:

src/shadowgen_training/data/AGENTS.md
Markdown
# AGENTS.md

This directory owns dataset schemas, manifests, splits, transforms, and quality checks.

Rules:
- Do not change sample schema casually.
- Preserve backward compatibility for manifest readers when possible.
- Any schema change must update:
  - `docs/dataset.md`
  - related tests
  - any manifest generation scripts
- Prefer explicit validation and helpful error messages.
- Do not mix training logic into data modules.
src/shadowgen_training/evaluation/AGENTS.md
Markdown
# AGENTS.md

This directory owns evaluation metrics, qualitative benchmarks, and reports.

Rules:
- Metrics must be deterministic for fixed inputs.
- Do not rename reported metrics without updating docs and tracking code.
- Qualitative visual panels should remain stable across runs for comparison.
- New metrics must include at least one focused test.
src/shadowgen_training/models/AGENTS.md
Markdown
# AGENTS.md

This directory owns model wrappers, adapters, and export helpers.

Rules:
- Keep architecture-specific code isolated by module.
- Avoid leaking tracker or CLI concerns into model code.
- Prefer registry/factory integration over one-off branching in callers.
- Any change affecting tensor shapes must update tests.
3) .codex/config.toml

OpenAI официально указывает, что проектные настройки Codex можно класть в .codex/config.toml, а CLI и IDE extension используют общие конфигурационные слои.
OpenAI разработчики
+1
нт:

TOML
model = "gpt-5.2-codex"
model_reasoning_effort = "medium"

approval_policy = "on-request"
sandbox_mode = "workspace-write"

project_doc = "README.md"

[profiles.default]
model = "gpt-5.2-codex"
model_reasoning_effort = "medium"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[profiles.review]
model = "gpt-5.2-codex"
model_reasoning_effort = "high"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[profiles.safe_refactor]
model = "gpt-5.2-codex"
model_reasoning_effort = "high"
approval_policy = "never"
sandbox_mode = "workspace-write"

Если какие-то поля в твоей версии Codex называются чуть иначе, ориентируйся на актуальный config reference OpenAI. Но сама идея именно такая: профиль для обычной работы, профиль для review, профиль для осторожного рефакторинга.
OpenAI разработчики
+1
блоны задач для Codex

Положи в .codex/prompts/ короткие task-шаблоны.

.codex/prompts/train-task.md
Markdown
Goal: improve or extend the training pipeline without breaking reproducibility.

Checklist:
- inspect existing Hydra configs
- inspect training CLI and engine modules
- make minimal localized changes
- add or update tests
- update docs if behavior changes
- report exact commands to validate the change
.codex/prompts/eval-task.md
Markdown
Goal: improve evaluation, metrics, or qualitative reporting.

Checklist:
- preserve metric naming unless change is intentional
- keep fixed eval subset stable
- add tests for new metrics
- update docs/evaluation.md if outputs change
.codex/prompts/refactor-task.md
Markdown
Goal: perform a safe refactor with minimal behavior change.

Checklist:
- preserve public CLI behavior
- avoid mixing responsibilities across modules
- do not move files unless the benefit is clear
- run lint and focused tests
- summarize risks and follow-up cleanup separately
Ещё 3 файла, которые очень помогут
docs/runbooks/local-setup.md

Пошаговый local setup:

uv sync

wandb login

dvc remote list

python -m shadowgen_training.cli.doctor

docs/runbooks/add-dataset-version.md

Как добавить новую версию датасета:

положить raw вне repo

прогнать prepare_dataset.py

собрать manifest

прогнать quality checks

зафиксировать processed версию через DVC

обновить configs/data/*.yaml

docs/runbooks/export-model-to-service.md

Как передать модель в ShadowGen-ML-service:

какой чекпоинт брать

какую команду запускать

куда складывается export

как проверить совместимость

Что бы я добавил в .gitignore
gitignore
# Python
__pycache__/
*.pyc

# Environments
.venv/

# Outputs
outputs/
multirun/
artifacts/reports/
artifacts/visualizations/
artifacts/exported/
tmp/

# Notebooks
.ipynb_checkpoints/

# ML artifacts
checkpoints/
wandb/
mlruns/

# Data
data/external/*
!data/external/.gitkeep

# DVC local temp
.dvc/tmp/
Что бы я добавил в README.md в самом начале
Markdown
# ShadowGen-ML-training

Training and evaluation pipeline for ShadowGen shadow generation models.

## Responsibilities
- dataset preparation and validation
- reproducible training runs
- evaluation and visual benchmarking
- experiment tracking
- model export for `ShadowGen-ML-service`

## Quick start
```bash
uv sync
python -m shadowgen_training.cli.doctor
pytest -q tests/test_train_smoke.py
python -m shadowgen_training.cli.train experiment=baseline_lora train=debug

---

# Что особенно важно именно для твоего проекта

Для ShadowGen я бы зафиксировал 4 инженерных принципа прямо в документации и `AGENTS.md`:

1. **Raw data never lives in Git**
2. **Every experiment has a fixed config name**
3. **Every model change must have qualitative shadow panels**
4. **Service export is a contract, not an ad hoc file dump**

Эти четыре правила реально удержат проект от расползания.

---

# Мой итог

Я бы рекомендовал:

- репозиторий обучения назвать **`ShadowGen-ML-training`**
- сделать его отдельным от `ShadowGen-ML-service`
- вести проект через
  - `AGENTS.md` в корне
  - локальные `AGENTS.md` в `data/`, `models/`, `evaluation/`
  - `.codex/config.toml`
  - `docs/runbooks/`
  - Hydra-конфиги как единственный источник правды для экспериментов

Это очень хорошо выглядит и для реальной работы, и для портфолио.

Дальше могу сразу собрать тебе **готовые тексты файлов**:
`README.md`, `AGENTS.md`, `.codex/config.toml`, `pyproject.toml`, `Makefile`, `dvc.yaml` и стартовые Hydra-конфиги под baseline LoRA.
::contentReference[oaicite:11]{index=11}

