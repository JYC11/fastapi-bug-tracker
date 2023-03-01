def set_pagination(query, page, count_per_page):
    offset = count_per_page * (page - 1)
    return query.offset(offset).limit(count_per_page)
