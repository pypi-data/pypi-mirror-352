GRAPHQL_URL = 'http://localhost:13337/graphql'

GET_OHM_CONFIG = """
	query {
		get_ohm_config {
			db {
				host
				port
				user
				database
				password
				sslmode
			}
			tables {
				metadata
				observation
				dataset_cycle
			}
		}
	}
"""
