import unittest
from robohome.houseSystem import Room, House


class MethCallLogger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True


class MockItem:
    def __init__(self, _id, name, brand, _type, ip):
        self._id = _id
        self.name = name
        self.brand = brand
        self._type = _type
        self.ip = ip

    def getState(self):
        return 1


class MockRoom:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.items = {}

    def getStructure(self):
        return {'id': self.id, 'name': self.name, 'items': []}


class MockHouse(House):
    def __init__(self):
        db = MockDatabase()
        super(MockHouse, self).__init__(db)
        self.item1 = MockItem(1, "mockName1", "mockBrand1", "mockType1", "mockIP1")
        self.item2 = MockItem(2, "mockName2", "mockBrand1", "mockType2", "mockIP2")
        self.item3 = MockItem(3, "mockName3", "mockBrand2", "mockType1", "mockIP3")
        self.item4 = MockItem(4, "mockName4", "mockBrand2", "mockType2", "mockIP4")

        self.room1 = MockRoom(1, "room1")
        self.room2 = MockRoom(2, "room2")

        self.room1.items = {1: self.item1, 2: self.item2}
        self.room2.items = {3: self.item3, 4: self.item4}

        self.rooms = {1: self.room1, 2: self.room2}

        self.event1 = MockEvent(1, "mockType1", self.item1, None, "mockTrigger", 1)
        self.event2 = MockEvent(2, "mockType2", self.item2, None, "mockTrigger", 1)
        self.event3 = MockEvent(3, "mockType2", self.item2, None, "mockTrigger2", 1)

        self.events = [self.event1, self.event2, self.event3]


class MockEvent:
    def __init__(self, id, type, item, room, trigger, enabled):
        self.id = id
        self.item = item
        self.type = type
        self.trigger = trigger
        self.enabled = enabled
        self.room = room
        self.conditions = []
        self.actions = []


class MockCondition:
    def __init__(self, result):
        self.result = result

    def check(self):
        return self.result


class MockAction:
    def __init__(self, allItemsInHouse=False, _type=""):
        self.allItemsInHouse = allItemsInHouse
        self.itemsForType = []
        self._type = _type

    def isAllItemsInHouse(self):
        return self.allItemsInHouse

    def doAction(self, itemsForType=[]):
        self.itemsForType = itemsForType


class MockRoomTable:

    def __init__(self):
        self.entries = []
        self.i = -1
        pass

    def addEntry(self, name):
        self.i += 1
        self.entries.append(MockRoom(self.i, name))
        return self.i

    def retrieveAllData(self):
        return ((1, "lounge"),)

    def updateEntry(self, id, name):
        pass


class MockTypesTable:

    def __init__(self):
        self.entries = []
        pass

    def getIdForName(self, type):
        return 1

    def getNameForId(self, id):
        return "motionSensor"


class MockItemsTable:

    i = -1

    def __init__(self):
        self.entries = []
        pass

    def addEntry(self, name, brand, ip, roomId, typeId):
        MockItemsTable.i += 1
        self.entries.append(MockItem(MockItemsTable.i, name, brand, typeId, ip))
        return MockItemsTable.i

    def retrieveForRoomId(self, id):
        return ((1, "sensor", "rf", "0.0.0.0", id, 1),)


class MockEventsTable:
    def getEvents(self):
        return ((1, "mockType", 1, 1, "mockTrigger", 1),)


class MockConditionsTable:
    def getConditionsForEvent(self, event):
        return ((1, 1, "mockSignature", "=", 1),)


class MockActionsTable:
    def getActionsForEvent(self, event):
        return ((1, 1, None, "mockSignature", "mockType"),)


class MockDatabase:

    def __init__(self):
        self.room = MockRoomTable()
        self.types = MockTypesTable()
        self.items = MockItemsTable()
        self.events = MockEventsTable()
        self.conditions = MockConditionsTable()
        self.actions = MockActionsTable()


class TestHouse(unittest.TestCase):

    def test_init(self):
        db = MockDatabase()
        h = House(db)
        self.assertEqual({}, h.rooms)
        self.assertEqual(db, h.database)

    def test_addRoom(self):
        db = MockDatabase()
        h = House(db)
        h.addRoom("lounge")
        self.assertEqual(h.rooms[db.room.i].id, db.room.entries[db.room.i].id)
        self.assertEqual(h.rooms[db.room.i].name, db.room.entries[db.room.i].name)

    def test_addItem(self):
        db = MockDatabase()
        h = House(db)
        h.addRoom("lounge")
        h.addItem(0, "sensor", "rf", "motionSensor", "0.0.0.0")
        self.assertEqual(h.rooms[db.room.i].items[MockItemsTable.i]._id, db.items.entries[MockItemsTable.i]._id)
        self.assertEqual(h.rooms[db.room.i].items[MockItemsTable.i].name, db.items.entries[MockItemsTable.i].name)
        self.assertEqual(h.rooms[db.room.i].items[MockItemsTable.i]._type, "motionSensor")
        self.assertEqual(h.rooms[db.room.i].items[MockItemsTable.i].brand, db.items.entries[MockItemsTable.i].brand)
        self.assertEqual(h.rooms[db.room.i].items[MockItemsTable.i].ip, db.items.entries[MockItemsTable.i].ip)

    def test_initFromDatabase(self):
        db = MockDatabase()
        h = House(db)
        h.initFromDatabase()
        self.assertEqual(h.rooms[1].name, "lounge")
        self.assertEqual(h.rooms[1].id, 1)

    def test_getRoomByItemId(self):
        db = MockDatabase()
        h = House(db)
        roomId = h.addRoom("lounge")
        id = 0
        itemId = h.addItem(id, "sensor", "rf", "motionSensor", "0.0.0.0")
        room = h.getRoomByItemId(itemId)
        self.assertEqual(room.name, "lounge")
        self.assertEqual(room.id, roomId)

    def test_getItemById(self):
        db = MockDatabase()
        h = House(db)
        h.addRoom("lounge")
        id = 0
        itemId = h.addItem(id, "sensor", "rf", "motionSensor", "0.0.0.0")
        item = h.getItemById(itemId)
        self.assertEqual(item.name, "sensor")
        self.assertEqual(item._type, "motionSensor")
        self.assertEqual(item._id, itemId)
        self.assertEqual(item.ip, "0.0.0.0")
        self.assertEqual(item.brand, "rf")

    def test_getItemByIP(self):
        h = MockHouse()
        self.assertEqual(h.getItemByIP("mockIP1"), h.item1)

    def test_getItemByIP_error(self):
        h = MockHouse()
        self.assertRaises(Exception, h.getItemByIP, "badIP")

    def test_getItemsByType(self):
        h = MockHouse()
        self.assertEqual([h.item1, h.item3], h.getItemsByType("mockType1"))

    def test_getEventsForTrigger(self):
        h = MockHouse()
        self.assertEqual(h.getEventsForTrigger(h.item2, "mockTrigger"), [h.event2])

    def test_getHouseStructure(self):
        db = MockDatabase()
        h = House(db)
        room = MockRoom(1, "lounge")
        h.rooms = {1: room}
        self.assertEqual(h.getStructure(), {'rooms': [{'id': 1, 'name': "lounge", 'items': []}]})

    def test_getHouseStructure_emptylist(self):
        db = MockDatabase()
        h = House(db)
        h.rooms = {}
        self.assertEqual(h.getStructure(), {'rooms': []})

    def test_reactToEvent_singleEvent(self):
        h = MockHouse()
        h.event1.conditions = [MockCondition(True)]
        action = MockAction()
        action.doAction = MethCallLogger(action.doAction)
        h.event1.actions = [action]

        h.reactToEvent("mockIP1", "mockTrigger")

        self.assertTrue(action.doAction.was_called)

    def test_reactToEvent_conditionNotMet(self):
        h = MockHouse()
        h.event1.conditions = [MockCondition(True), MockCondition(False)]
        action = MockAction()
        action.doAction = MethCallLogger(action.doAction)
        h.event1.actions = [action]

        h.reactToEvent("mockIP1", "mockTrigger")

        self.assertFalse(action.doAction.was_called)

    def test_reactToEvent_allInHouse(self):
        h = MockHouse()
        action = MockAction(True, "mockType1")
        h.event1.actions = [action]
        h.reactToEvent("mockIP1", "mockTrigger")
        self.assertNotEqual(action.itemsForType, [])

    def test_executeMethod(self):
        db = MockDatabase()
        h = House(db)
        item1 = MockItem(1, "mockName", "mockBrand", "motionSensor", "mockIP")
        room = MockRoom(1, "lounge")
        room.items = {1: item1}
        h.rooms = {1: room}
        self.assertEqual(h.executeMethod(1, 1, "getState"), 1)

    def test_executeMethod_methodDoesNotExist(self):
        db = MockDatabase()
        h = House(db)
        item1 = MockItem(1, "mockName", "mockBrand", "motionSensor", "mockIP")
        room = MockRoom(1, "lounge")
        room.items = {1: item1}
        h.rooms = {1: room}
        self.assertRaises(AttributeError, h.executeMethod, 1, 1, "open")

    def test_executeMethod_itemDoesNotExist(self):
        db = MockDatabase()
        h = House(db)
        room = MockRoom(1, "lounge")
        room.items = {}
        h.rooms = {1: room}
        self.assertRaises(KeyError, h.executeMethod, 1, 1, "getState")

    def test_executeMethod_roomDoesNotExist(self):
        db = MockDatabase()
        h = House(db)
        h.rooms = {}
        self.assertRaises(KeyError, h.executeMethod, 1, 1, "getState")

    def test_updateRoom(self):
        db = MockDatabase()
        h = House(db)
        room = MockRoom(1, "lounge")
        h.rooms = {1: room}
        h.updateRoom(1, "new name")
        self.assertEqual(h.rooms[1].name, "new name")

class TestRoom(unittest.TestCase):

    def test_init(self):
        _id = 1
        name = "test"
        r = Room(_id, name)
        self.assertEqual(_id, r.id)
        self.assertEqual(name, r.name)
        self.assertEqual({}, r.items)

    def test_addItem(self):
        item = MockItem(1, 'a', 'a', 'a', '1')
        _id = 1
        name = "test"
        r = Room(_id, name)
        r.addItem(1, item)
        self.assertEqual(item, r.items[1])
        self.assertEqual(len(r.items), 1)

    def test_getStrucutre(self):
        item = MockItem(1, 'a', 'a', 'a', '1')
        _id = 1
        name = "test"
        r = Room(_id, name)
        r.addItem(1, item)
        self.assertEqual(r.getStructure(), {'id': 1, 'name': "test", 'items': [{'id': 1, 'name': 'a', 'type': 'a', 'brand': 'a', 'ip': '1'}]})

    def test_getStrucutre_noItems(self):
        _id = 1
        name = "test"
        r = Room(_id, name)
        self.assertEqual(r.getStructure(), {'id': 1, 'name': "test", 'items': []})

if __name__ == '__main__':
    unittest.main()
