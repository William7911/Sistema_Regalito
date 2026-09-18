-- fix_encoding.sql
-- Restaura los textos correctos (UTF-8) de los catálogos semilla del DERCAS.
-- Corrige los caracteres corruptos (acentos y eñes) que se grabaron como "??"
-- al aplicar init.sql mediante PowerShell con una codificación incorrecta.
--
-- Aplicar desde la raíz del proyecto (contenedor regalito_db):
--   docker cp .\database\fix_encoding.sql regalito_db:/tmp/fix_encoding.sql
--   docker exec -e PGPASSWORD=Regalito_2026 regalito_db psql -U regalito_admin -d regalito_pos -v ON_ERROR_STOP=1 -f /tmp/fix_encoding.sql
--
-- (docker cp copia los bytes tal cual: evita que PowerShell vuelva a corromper
--  la codificación al canalizar por stdin.)

BEGIN;

UPDATE categoria SET nombre = 'Cristalería' WHERE id_categoria = 1;
UPDATE categoria SET nombre = 'Ropa'        WHERE id_categoria = 2;
UPDATE categoria SET nombre = 'Juguetes'    WHERE id_categoria = 3;
UPDATE categoria SET nombre = 'Hogar'       WHERE id_categoria = 4;

UPDATE subcategoria SET nombre = 'Vasos'          WHERE id_subcategoria = 1;
UPDATE subcategoria SET nombre = 'Floreros'        WHERE id_subcategoria = 2;
UPDATE subcategoria SET nombre = 'Ropa Bebé'       WHERE id_subcategoria = 3;
UPDATE subcategoria SET nombre = 'Muñecas'         WHERE id_subcategoria = 4;
UPDATE subcategoria SET nombre = 'Deco Hogar'      WHERE id_subcategoria = 5;

UPDATE producto SET nombre = 'Vestido de Niña 2T'          WHERE id_producto = 2;
UPDATE producto SET nombre = 'Muñeca de Trapo Artesanal'   WHERE id_producto = 3;

COMMIT;