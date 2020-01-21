
itemName, groupName = 'Missing', 'Missing'
try:
    item_type_id = item['item_type_id']
    try:
        item_group_id = typeIDs[item_type_id]['groupID']
        try:
            itemName = typeIDs[item_type_id]['name']['en']
            try:
                groupName = groupIDs[item_group_id]['name']['en']
            except:
                pass
        except:
            pass
    except:
        pass
except:
    pass
finally:
    itemList.append((itemName, groupName))