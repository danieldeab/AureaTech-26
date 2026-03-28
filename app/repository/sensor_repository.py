def _row_to_sensor(self, row) -> Sensor:
    """Evita duplicar la lógica de mapeo en cada método."""
    return Sensor(
        sensor_id=row[0],
        from_community_id=row[1],
        type=row[2],
        location=row[3],
        is_enabled=bool(row[4]),
        created_at=row[5],  # TIMESTAMP ya viene como datetime desde la BD
    )

def add_sensor(self, sensor: Sensor) -> None:
    self.db.insert("sensors", sensor.to_row())  # sensor_id lo genera la BD

def get_all(self) -> List[Sensor]:
    data = self.db.select("sensors", "*", "*")
    return [self._row_to_sensor(row) for row in data]

def find_by_id(self, sensor_id: int) -> Optional[Sensor]:
    response = self.db.select("sensors", "sensor_id", sensor_id)
    return self._row_to_sensor(response[0]) if response else None

def save(self, sensor: Sensor) -> None:
    existing = self.db.select("sensors", "sensor_id", sensor.sensor_id)
    if existing:
        self.db.update("sensors", "sensor_id", sensor.sensor_id, sensor.to_row())
    else:
        self.db.insert("sensors", sensor.to_row())