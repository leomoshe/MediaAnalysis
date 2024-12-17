from collections import namedtuple
import time
import datetime
R2L = '\u202b'
NEW_LINE = '\n'
ITEMS_ENTITY_SEP = ';'


def srt2secs(data):
    ftime = time.strptime(data.split(',')[0], '%H:%M:%S')
    seconds = int(datetime.timedelta(hours=ftime.tm_hour, minutes=ftime.tm_min, seconds=ftime.tm_sec).total_seconds())
    return str(seconds)


def set_labels(labels, value, line_entities):
    for label in labels:
        try:
            value.append(ITEMS_ENTITY_SEP.join(line_entities.get(label, '')))
        except Exception as error:
            print(error)
    return value


SbtStartEnd = namedtuple("SbtStartEnd", ["subtitle", "start", "end"])
def srt2sbt_s_e(text) -> list[SbtStartEnd]:
    idx = 0
    items = []
    try:
        while idx < len(text):
            index = text[idx]
            idx += 1
            ranges = text[idx].split(' --> ')
            start = srt2secs(ranges[0])
            end = srt2secs(ranges[1])
            idx += 1
            subtitle = ''
            while idx < len(text) and text[idx] != '':
                if subtitle != '':
                    subtitle += ' '
                subtitle += text[idx]
                idx += 1
            #item = f"{start}{csv_separator}{end}{csv_separator}{subtitle}"
            #idx += 1
            #items.append(item + NEW_LINE)
            if subtitle != '':
                item = SbtStartEnd(subtitle=subtitle, start=start, end=end)
                items.append(item)
            idx += 1
    except Exception as error:
        print(error)
    return items


SbtLabels = namedtuple("SbtLabels", ["subtitle", "labels"])
# Subtitle and his labels
def create_sbt_entities(extract_entities, nlp, logger, text: list[SbtStartEnd]) -> tuple[list[SbtLabels], set]:
    entities: list[SbtLabels] = []
    labels = set()
    logger.info(f"{len(text)} items")

    for idx, item in enumerate(text):
        sentence = item.subtitle.replace(R2L, '').replace(NEW_LINE, '')
        sentence_labels = extract_entities(nlp, sentence)
        logger.info(f"{idx}; Text: {sentence}, Labels: {sentence_labels}")
        entities.append(SbtLabels(subtitle=sentence, labels=sentence_labels))
        for sentence_label in sentence_labels:
            labels.add(sentence_label)
    return entities, labels


def create_raw_entities(sent_s_e: list[SbtStartEnd], entities: list[SbtLabels], labels: set) -> list[list[str]]:
    result = [["mediatext", "start", "end", *[item for item in labels]]]
    for index, item in enumerate(entities):
        if sent_s_e[index].subtitle != '' and sent_s_e[index].subtitle is not None:
            value = [sent_s_e[index].subtitle, sent_s_e[index].start, sent_s_e[index].end]
            result.append(set_labels(labels, value, item.labels))
    return result


EntityItem = namedtuple("EntityItem", ["subtitle", "start", "end", "labels"])
def create_entities(labels_map, sent_s_e: list[SbtStartEnd], entities: list[SbtLabels], used_labels_keys: set) -> list[list[str]]:
    current_labels_map = {key: value for key, value in labels_map.items() if key in used_labels_keys}
    labels_title = list({value for value in current_labels_map.values()})
    entitiesItems: list[EntityItem] = []
    for index, entity in enumerate(entities):
        if sent_s_e[index].subtitle != '' and sent_s_e[index].subtitle is not None:
            labels = {key: [] for key in labels_title}
            for entity_label, values in entity.labels.items():
                mapped_label = labels_map.get(entity_label)
                if mapped_label:
                    current_values = labels.get(mapped_label, set())
                    labels[mapped_label].extend(values)


            entityItem = EntityItem(subtitle=sent_s_e[index].subtitle, start=sent_s_e[index].start, end=sent_s_e[index].end, labels=labels)
            entitiesItems.append(entityItem)

    result = [["mediatext", "start", "end", *labels_title]]
    for entityItem in entitiesItems:
        if entityItem.subtitle != '' and entityItem.subtitle is not None:
            #valuesEntities = {key: ';'.join(values) for key, values in entityItem.labels.items()}.values()
            valuesEntities = [';'.join(set(values)) for values in entityItem.labels.values()]
            res_item = [entityItem.subtitle, entityItem.start, entityItem.end] + valuesEntities
            result.append(res_item)
    return result
