GRAPHQL_URL = 'https://graph.maia.byterat.io/graphql'

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
