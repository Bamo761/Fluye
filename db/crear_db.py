from db.connection import get_connection

def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula REAL NOT NULL,
            direccion TEXT,
            placa TEXT,
            sector TEXT,
            correo TEXT,
            telefono TEXT,
            coordenada_x REAL,
            coordenada_y REAL,
            activo INTEGER DEFAULT 1
        )
    """)

    # Tabla intermediarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intermediarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto REAL NOT NULL
        )
    """)




    # Tabla deudas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deudas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            intermediario_id INTEGER,
            monto REAL,
            frecuencia_pago TEXT DEFAULT 'mensual',  -- mensual, quincenal, semanal, diari
            interes REAL,
            cantidad_pagos INTEGER,
            pagos_de_gracia INTEGER DEFAULT 0,
            fecha_inicio TEXT,
            tipo_prestamo TEXT DEFAULT 'simple',  -- 'simple', 'compuesto', 'frances', etc.
            cuota_fija REAL,
            cuotas_totales INTEGER,
            monto_total REAL,
            tasa_mora REAL,
            estado TEXT DEFAULT 'activa',
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (intermediario_id) REFERENCES intermediarios(id)
        )
    """)

    #tabla cronogramas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cronograma_pagos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            deuda_id INTEGER,
            n_cuota INTEGER,
            fecha TEXT,
            cuota REAL,
            interes REAL,
            abono REAL,
            saldo_restante REAL,
            estado TEXT DEFAULT 'pendiente',
            FOREIGN KEY(cliente_id) REFERENCES clientes(id),
            FOREIGN KEY(deuda_id) REFERENCES deudas(id)
        )
    """)

    # Tabla abonos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deuda_id INTEGER,
            fecha TEXT,
            monto REAL,
            observacion TEXT,
            FOREIGN KEY (deuda_id) REFERENCES deudas(id)
        )
    """)

    #tabla refinanciación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refinanciaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deuda_original_id INTEGER,
            deuda_nueva_id INTEGER,
            fecha_refinanciamiento TEXT,
            tipo_reduccion TEXT, 
            observacion TEXT,
            FOREIGN KEY (deuda_original_id) REFERENCES deudas(id),
            FOREIGN KEY (deuda_nueva_id) REFERENCES deudas(id)
        )
    """)
    #tabla mora
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            deuda_id INTEGER,
            fecha TEXT,               -- Un día puntual de mora
            monto_faltante REAL,      -- Lo que quedó sin pagar ese día
            tasa_mora REAL,           -- La tasa diaria aplicada ese día
            mora_calculada REAL,      -- El monto de mora generado ese día
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (deuda_id) REFERENCES deudas(id)
        )
    """)

    # Tabla configuraciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)

    # Tabla notas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha TEXT,
            texto TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente.")

