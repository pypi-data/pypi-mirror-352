#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APIMA56XXT.py

Clase para conectarse a una OLT vía Telnet y, además de obtener:
  - Slots (tarjetas PON)
  - Puertos GPON de cada slot
  - ONTs de cada puerto

Amplía la funcionalidad para que, en ONTs con estado "Online", consulte por SNMP asíncrono (pysnmp ≥6.2):
  - Potencia TX (ptx)
  - Potencia RX (prx)
  - (Opcional) Temperatura

Maneja prompts dinámicos, paginación y confirmaciones.
"""

import telnetlib
import re
import asyncio

from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    UdpTransportTarget,
)

from pprint import pprint


class UserBusyError(Exception):
    """Raised when la OLT indica que los intentos de login están bloqueados."""
    pass


class APIMA56XXT:
    """
    Clase para conectarse a una OLT vía Telnet y, además de obtener:
      - Slots (tarjetas PON)
      - Puertos GPON de cada slot
      - ONTs de cada puerto

    Amplía la funcionalidad para que, en ONTs con estado "Online", consulte por SNMP:
      - Potencia TX (ptx)
      - Potencia RX (prx)
      - (Opcional) Temperatura

    Maneja prompts dinámicos, paginación y confirmaciones.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        prompt: str,
        snmp_ip: str,
        snmp_port: int,
        snmp_community: str,
        timeout: float = 2.0,
        debug: bool = False,
    ):
        # Parámetros Telnet
        self.host = host
        self.user = user
        self.password = password
        self.timeout = timeout
        self.debug = debug
        self.tn = None

        # Regex para detectar prompt dinámico (p.ej. MA5603T>, MA5603T(config)#, etc.)
        pattern = rf"^{re.escape(prompt)}(?:\([^)]+\))?[>#]"
        self.prompt_re = re.compile(pattern)

        # Parámetros SNMP
        self.snmp_ip = snmp_ip
        self.snmp_port = snmp_port or 161
        self.snmp_community = snmp_community

    def _log(self, *args):
        if self.debug:
            print("[DEBUG]", *args)

    def _read_line(self) -> str:
        raw = self.tn.read_until(b"\n", timeout=self.timeout)
        text = raw.decode("utf-8", errors="ignore")
        # Quitamos cualquier código ANSI y el salto de línea final
        return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text).rstrip()

    def _read_until_prompt(self) -> str:
        """
        Lee líneas hasta detectar el prompt dinámico,
        gestionando paginación, errores o advertencias de usuario bloqueado.
        """
        lines = []
        while True:
            line = self._read_line()
            if not line:
                continue

            # Si detectamos bloqueo por demasiados intentos de login:
            if "Reenter times have reached the upper limit" in line:
                self._log("Usuario bloqueado: demasiados intentos de reingreso")
                self.close()
                raise UserBusyError("Usuario ocupado: demasiados intentos de login")

            lines.append(line)
            if self.debug:
                print("[DEBUG] →", line)

            # Si la línea empieza con '%' suele indicar un mensaje de error/síntaxis inválida
            if line.startswith('%'):
                break

            # Si aparece paginación, enviamos ENTER y seguimos leyendo
            if 'More' in line or "Press 'Q'" in line or '---- More' in line:
                self._log("Paginación detectada, ENTER")
                self.tn.write(b"\n")
                continue

            # Si coincide con el prompt dinámico, terminamos la lectura
            if self.prompt_re.search(line):
                break

        return "\n".join(lines)

    def connect(self):
        """Conecta por Telnet, hace login, entra en modo enable y luego en modo config."""
        self._log("Conectando a", self.host)
        self.tn = telnetlib.Telnet(self.host)

        # Login usuario
        self.tn.read_until(b"User name:", timeout=self.timeout)
        self.tn.write(self.user.encode() + b"\n")
        self.tn.read_until(b"User password:", timeout=self.timeout)
        self.tn.write(self.password.encode() + b"\n")

        # Esperar prompt de usuario
        self._read_until_prompt()

        # Entrar en modo enable
        self._send('enable')
        self._read_until_prompt()

        # Entrar en modo config
        self._send('config')
        self._read_until_prompt()

        print("Conectado en modo config")

    def close(self):
        """Cierra la conexión Telnet (sin pasos de confirmación extra)."""
        if self.tn:
            self.tn.close()
        self.tn = None
        self._log("Desconectado")

    def disconnect(self):
        """
        Sale de interfaces/config/enable y cierra la conexión Telnet con confirmación.
        Si ya está cerrado (self.tn es None), no hace nada.
        """
        if not self.tn:
            return

        # 1) Quit interfaces GPON
        self._send('quit')
        self._read_until_prompt()

        # 2) Quit config
        self._send('quit')
        self._read_until_prompt()

        # 3) Quit enable (pide confirmación "y/n")
        self._send('quit')
        try:
            confirm = self.tn.read_until(b"(y/n)", timeout=self.timeout).decode('utf-8', errors='ignore')
            self._log(f"Confirm prompt: {confirm.strip()}")
            self.tn.write(b"y\n")
        except Exception:
            pass

        # Finalmente cerrar socket
        self.tn.close()
        self.tn = None
        self._log("Desconectado")

    def _send(self, cmd: str):
        """Envía un comando Telnet (sin esperar prompt previo)."""
        self._log(f"Enviando comando: {cmd}")
        self.tn.write(cmd.encode() + b"\n")

    def get_slots(self) -> list[tuple[str, str]]:
        """
        Obtiene la lista de slots (tarjetas PON) con su tipo,
        ejecutando "display board 0" en Telnet.
        Devuelve una lista de tuplas: [(slot_str, tipo_str), ...].
        """
        self._send('display board 0')
        raw = self._read_until_prompt()
        slots = []
        for line in raw.splitlines():
            # Ejemplo de línea: "  0   H0GPBD   PON board"
            m = re.match(r"\s*(\d+)\s+H\d+([A-Z]+)", line)
            if m:
                slots.append((m.group(1), m.group(2)))
        return slots

    def get_ports(self, slot: str) -> list[dict]:
        """
        Obtiene los puertos GPON de un slot concreto.
        - Entra en "interface gpon 0/{slot}"
        - Lanza "display port state all"
        - Parsea cada bloque que empieza por "F/S/P"
        - Sale con "quit"
        Devuelve una lista de diccionarios con la info de cada puerto.
        """
        self._send(f'interface gpon 0/{slot}')
        self._read_until_prompt()
        self._send('display port state all')
        raw = self._read_until_prompt()

        ports = []
        # Cada bloque de un puerto empieza con "F/S/P"
        for bloque in raw.split('F/S/P')[1:]:
            info = self._parse_port_block(slot, bloque)
            if info:
                ports.append(info)

        # Salir de "interface gpon"
        self._send('quit')
        self._read_until_prompt()
        return ports

    async def get_onts(self, slot: str, port_id: int) -> list[dict]:
        """
        Obtiene la lista de ONTs conectadas a un puerto GPON:
        - Entra en "interface gpon 0/{slot}"
        - Lanza "display ont info {port_id} all"
        - Parsea la tabla de ONTs
        - Sale de "interface gpon"
        Además, para cada ONT cuyo run_state sea "online", llama a SNMP y añade
        'ptx' y 'prx' al diccionario de dicha ONT.
        """
        self._send(f'interface gpon 0/{slot}')
        self._read_until_prompt()

        self._send(f'display ont info {port_id} all')
        raw = self._read_until_prompt()

        # Salir de "interface gpon"
        self._send('quit')
        self._read_until_prompt()

        # Parsear la sección ONT (sin SNMP aún)
        onts = self._parse_onts(raw, slot, port_id)

        # Para cada ONT «online», obtener ptx/prx por SNMP
        for ont in onts:
            if ont.get('run_state', '').lower() == 'online':
                try:
                    ptx = await self._snmp_potencia_tx(slot, port_id, ont['id'])
                    prx = await self._snmp_potencia_rx(slot, port_id, ont['id'])
                    ont['ptx'] = ptx
                    ont['prx'] = prx
                    # Si quisieras añadir temperatura:
                    # ont['temp'] = await self._snmp_temperatura(slot, port_id, ont['id'])
                except Exception as e:
                    self._log(f"Error SNMP ONT {slot}/{port_id}/{ont['id']}: {e}")
                    ont['ptx'] = ""
                    ont['prx'] = ""
            else:
                ont['ptx'] = ""
                ont['prx'] = ""
        return onts

    async def scan_all(self) -> list[dict]:
        """
        Escaneo completo:
          1. Obtiene todos los slots con get_slots()
          2. Para cada slot tipo "GPBD", obtiene puertos GPON con get_ports(slot)
          3. Para cada puerto cuya 'optical_state' sea "Online", llama a get_onts(...)
        Devuelve lista de dicts:
          [ { 'id': slot, 'tipo': tipo, 'ports': [ {port_info, onts: [...]}, ... ] }, ... ]
        """
        result = []
        for slot, tipo in self.get_slots():
            entry = {'id': slot, 'tipo': tipo, 'ports': []}
            if tipo == 'GPBD':
                for port in self.get_ports(slot):
                    if port.get('optical_state', '').lower() == 'online':
                        port['onts'] = await self.get_onts(slot, port['id'])
                    else:
                        port['onts'] = []
                    entry['ports'].append(port)
            result.append(entry)
        return result

    def _parse_port_block(self, slot: str, bloque: str) -> dict | None:
        """
        Parsea un bloque de salida de "display port state all" para un slot dado.
        Cada bloque tiene líneas como:
           F/S/P      0/0/1
            Optical Module status   Online
            Port state              Up
            Laser state             Normal
            ...
        Devuelve un dict con campos: id, schema_fsp, optical_state, port_state, laser_state, etc.
        """
        lines = bloque.strip().splitlines()
        m = re.match(rf"\s*0/{re.escape(slot)}/(\d+)", lines[0])
        if not m:
            return None
        pid = int(m.group(1))
        data = {
            'id': pid,
            'schema_fsp': f"0/{slot}/{pid}",
            'optical_state': None,
            'port_state': None,
            'laser_state': None,
            'bw': None,
            'temperature': None,
            'tx_bias': None,
            'voltage': None,
            'tx_power': None,
            'illegal_rogue_ont': None,
            'max_distance': None,
            'wave_length': None,
            'fiber_type': None,
            'length': None,
        }
        for l in lines:
            if 'Optical Module status' in l:
                data['optical_state'] = l.split()[-1]
            elif 'Port state' in l:
                data['port_state'] = l.split()[-1]
            elif 'Laser state' in l:
                data['laser_state'] = l.split()[-1]
            elif 'Available bandwidth' in l:
                data['bw'] = l.split()[-1]
            elif 'Temperature' in l:
                data['temperature'] = l.split()[-1]
            elif 'TX Bias' in l:
                data['tx_bias'] = l.split()[-1]
            elif 'Supply Voltage' in l:
                data['voltage'] = l.split()[-1]
            elif 'TX power' in l:
                data['tx_power'] = l.split()[-1]
            elif 'Illegal rogue ONT' in l:
                data['illegal_rogue_ont'] = l.split()[-1]
            elif 'Max Distance' in l:
                data['max_distance'] = l.split()[-1]
            elif 'Wave length' in l:
                data['wave_length'] = l.split()[-1]
            elif 'Fiber type' in l:
                data['fiber_type'] = l.split()[-1]
            elif 'Length' in l:
                data['length'] = l.split()[-1]
        return data

    def _parse_onts(self, raw: str, slot: str, port_id: int) -> list[dict]:
        """
        Parsea la salida de "display ont info {port_id} all".
        Devuelve una lista de ONTs con campos:
          id (ONT-ID), schema_fsp, sn, control_flag, run_state, config_state, match_state, protect_side, description.
        """
        onts = []
        lines = raw.splitlines()
        in_main = False
        in_desc = False
        base_fsp = f"0/{slot}/{port_id}"

        for ln in lines:
            # Inicio sección principal de ONTs (tabla)
            if ln.startswith('  F/S/P') and 'ONT' in ln and 'SN' in ln:
                in_main = True
                continue

            # Si estamos en la sección principal y la línea no está vacía → parsear fila
            if in_main and ln.strip():
                parts = ln.split()
                # Formato esperado:
                # ['F/S/P', '0/0/1', 'ONT_ID', 'SN', 'CTRL', 'RUN', 'CFG', 'MATCH', 'PROTECT']
                if len(parts) >= 9 and parts[1].startswith(f"{slot}/"):
                    try:
                        oid = int(parts[2])
                    except ValueError:
                        continue
                    entry = {
                        'id': oid,
                        'schema_fsp': base_fsp,
                        'sn': parts[3],
                        'control_flag': parts[4],
                        'run_state': parts[5],    # p.ej. "online" o "offline"
                        'config_state': parts[6],
                        'match_state': parts[7],
                        'protect_side': parts[8],
                        'description': None
                    }
                    onts.append(entry)
                    continue

            # Si empieza la sección de descripción (vuelve a verse 'F/S/P' pero con 'Description')
            if ln.startswith('  F/S/P') and 'Description' in ln:
                in_desc = True
                in_main = False
                continue

            # Si estamos en sección de descripción y la línea no está vacía → asociar descripción
            if in_desc and ln.strip():
                parts = ln.split(maxsplit=3)
                if len(parts) == 4 and parts[0].startswith('0/'):
                    try:
                        oid = int(parts[2])
                    except ValueError:
                        continue
                    desc = parts[3]
                    for o in onts:
                        if o['id'] == oid:
                            o['description'] = desc
                            break

        return onts

    async def _consultagetsnmp(self, codigo_oid: str):
        """
        Ejecuta un GET SNMP al OID completo de forma asíncrona.
        Devuelve el valor (entero) o None si hay error/timeout.
        """
        # Creamos el transport asíncrono con timeout=1 seg y retries=0
        transport = await UdpTransportTarget.create(
            (self.snmp_ip, self.snmp_port),
            timeout=1,
            retries=0
        )

        iterator = get_cmd(
            SnmpEngine(),
            CommunityData(self.snmp_community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(codigo_oid))
        )
        error_indication, error_status, error_index, var_binds = await iterator

        if error_indication or error_status:
            return None

        for var_bind in var_binds:
            return var_bind[1]
        return None

    async def _snmp_potencia_tx(self, slot: int | str, port: int, ont: int) -> float | str:
        """
        Devuelve la potencia TX (mW) para la ONT indicada, de forma asíncrona:
         - OID base: .1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6.<código_base><ont>
         - El valor SNMP se divide entre 1000 y se redondea a 2 decimales.
         - Si viene 2147483647 o -0.0, devuelve cadena vacía.
         - Si hay error, devuelve cadena vacía.
        """
        cod1 = ".1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6."
        cod2 = self._calcular_codigo(slot, port) + str(ont)
        oid_full = cod1 + cod2

        valor = await self._consultagetsnmp(oid_full)
        if valor is None:
            return ""
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            return ""
        poten = float(valor) / 1000
        poten = round(poten, 2)
        if val_int == 2147483647 or poten == -0.0:
            return ""
        return poten

    async def _snmp_potencia_rx(self, slot: int | str, port: int, ont: int) -> float | str:
        """
        Devuelve la potencia RX (dBm) para la ONT indicada, de forma asíncrona:
         - OID base: .1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4.<código_base><ont>
         - El valor SNMP se divide entre 100 y se redondea a 2 decimales.
         - Si viene 2147483647 o -0.01, devuelve cadena vacía.
         - Si hay error, devuelve cadena vacía.
        """
        cod1 = ".1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4."
        cod2 = self._calcular_codigo(slot, port) + str(ont)
        oid_full = cod1 + cod2

        valor = await self._consultagetsnmp(oid_full)
        if valor is None:
            return ""
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            return ""
        poten = float(valor) / 100
        poten = round(poten, 2)
        if val_int == 2147483647 or poten == -0.01:
            return ""
        return poten

    def _calcular_codigo(self, slot: int | str, pon: int | str) -> str:
        """
        A partir de slot y PON calcula la parte numérica base del OID:
        base (4194304000) + pon_int * 256 + slot_int * 8192, devolviendo "<valor>.".
        """
        slot_int = int(slot)
        pon_int = int(pon)
        num = 4194304000
        codigo = num + pon_int * 256 + slot_int * 8192
        return str(codigo) + "."

    # Ejemplo opcional para temperatura, similar a TX/RX:
    # async def _snmp_temperatura(self, slot: int | str, port: int, ont: int) -> float | str:
    #     """
    #     Devuelve la temperatura de la ONT, de forma asíncrona:
    #      - OID base: .1.3.6.1.4.1.2011.6.128.1.1.2.51.1.1.<código_base><ont>
    #      - Si viene 2147483647 o valor < 0, devuelve cadena vacía.
    #      - Si hay error, devuelve cadena vacía.
    #     """
    #     cod1 = ".1.3.6.1.4.1.2011.6.128.1.1.2.51.1.1."
    #     cod2 = self._calcular_codigo(slot, port) + str(ont)
    #     oid_full = cod1 + cod2
    #
    #     valor = await self._consultagetsnmp(oid_full)
    #     if valor is None:
    #         return ""
    #     try:
    #         val_int = int(valor)
    #     except (ValueError, TypeError):
    #         return ""
    #     temp = float(valor)
    #     temp = round(temp, 2)
    #     if val_int == 2147483647 or temp < 0:
    #         return ""
    #     return temp


if __name__ == '__main__':
    api = APIMA56XXT(
        host='192.168.88.25',
        user='root',
        password='admin',
        prompt='MA5603T',
        snmp_ip='192.168.88.25',
        snmp_port=161,
        snmp_community='public',
        debug=True
    )

    async def main():
        try:
            api.connect()                    # Conexión Telnet (síncrona)
            full = await api.scan_all()      # scan_all es asíncrono
            pprint(full)
        except UserBusyError as e:
            print(f"ERROR: {e}")
        finally:
            api.close()                      # Cerrar Telnet

    asyncio.run(main())
