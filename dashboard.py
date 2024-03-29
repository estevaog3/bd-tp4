import psycopg2
import sys
from terminaltables import AsciiTable

def show_results_as_table(rows, column_names):
	rows = [list(row) for row in rows]
	rows.insert(0, column_names)
	ascii_table = AsciiTable(rows)
	print(ascii_table.table)

if __name__ == '__main__':

	if(len(sys.argv) != 5):
		print("Erro! Este programa deve ser executado assim:")
		print("python3 dashboard.py <endereço-do-servidor> <usuario> <senha> <nome-do-BD>")
		sys.exit(1)

	try:
		con = None
		host = sys.argv[1]
		user = sys.argv[2]
		password = sys.argv[3]
		database = sys.argv[4]
		con = psycopg2.connect(host=host, database=database, user=user, password=password)
		cur = con.cursor()

		con.commit()
		print('Nota: Nas consultas onde se diz "dado um produto", o produto cujo id vale 2 foi utilizado')
		print("Consultas:")
		print("Dado produto, listar os 5 comentários mais úteis e com maior avaliação e os 5 comentários mais úteis e com menor avaliação:")
		cur.execute("(SELECT helpful, rating, product_id, customer_id, _date FROM REVIEW  WHERE product_id=2 ORDER BY helpful DESC, rating DESC LIMIT 5) UNION ALL (SELECT helpful, rating, product_id, customer_id, _date FROM REVIEW WHERE product_id=2 ORDER BY rating ASC, helpful DESC LIMIT 5)")
		rows = cur.fetchall()
		show_results_as_table(rows, ['helpful', 'rating', 'product_id', 'customer_id', 'date'])
		print()

		print("Dado um produto, listar os produtos similares com maiores vendas do que ele:")
		cur.execute("SELECT P2.* FROM PRODUCT P1, PRODUCT P2, PRODUCT_SIMILAR PS WHERE P1.id = 2 AND PS.product_id = P1.id AND PS.similar_asin = P2.asin AND P2.salesrank < P1.salesrank")
		rows = cur.fetchall()
		show_results_as_table(rows, ['title', 'id', 'asin', 'group', 'salesrank'])
		print()

		print("Dado um produto, mostrar a evolução diária das médias de avaliação ao longo do intervalo de tempo coberto no arquivo de entrada:")
		cur.execute("SELECT title, _date, avg(rating) FROM product, review WHERE product.id = 2 and product_id = 2 GROUP BY title, _date")
		rows = cur.fetchall()
		show_results_as_table(rows, ['title', 'date', 'avg(rating)'])
		print()

		print("Listar os 10 produtos lideres de venda em cada grupo de produtos:")
		cur.execute("WITH ranking AS (SELECT id,_group,   salesrank, RANK() OVER (PARTITION BY _group ORDER BY salesrank ASC) product_rank FROM PRODUCT WHERE salesrank >= 1)SELECT P._group, P.salesrank, P.title FROM ranking R, PRODUCT P WHERE P.id=R.id AND P._group=R._group AND R.product_rank <= 10 ORDER BY P._group, salesrank ASC")
		rows = cur.fetchall()
		show_results_as_table(rows, ['group' , 'salesrank' , 'title'])
		print()

		print("Listar os 10 produtos com a maior média de avaliações úteis positivas por produto:")
		cur.execute("SELECT title, avg(helpful) FROM product, review WHERE product.id = product_id GROUP BY title ORDER BY avg(helpful) DESC LIMIT 10")
		rows = cur.fetchall()
		show_results_as_table(rows, ['title', 'avg(helpful)'])
		print()

		print("Listar a 5 categorias de produto com a maior média de avaliações úteis positivas por produto:")
		cur.execute("SELECT name,avg(helpful) FROM category, review WHERE category.id = product_id GROUP BY name ORDER BY avg(helpful) DESC LIMIT 5;")
		rows = cur.fetchall()
		show_results_as_table(rows, ['name', 'avg(helpful)'])
		print()

		print("Listar os 10 clientes que mais fizeram comentários por grupo de produto:")
		cur.execute("SELECT T._group, T.count, T.customer_id FROM (SELECT P._group, RANK() OVER (PARTITION BY P._group ORDER BY COUNT(*) DESC, R.customer_id), COUNT(*), R.customer_id FROM REVIEW R, PRODUCT P WHERE P.id=R.product_id GROUP BY R.customer_id, P._group ORDER BY P._group, COUNT(*) DESC) AS T WHERE T.rank <= 10 ORDER BY T._group, T.rank")
		rows = cur.fetchall()
		show_results_as_table(rows, ['group', 'number_of_comments', 'customer_id'])

	except psycopg2.DatabaseError as e:
		if(con):
		    con.rollback()
		print(f'Error {e}')
		sys.exit(1)

	finally:
		if(con):
			con.close()