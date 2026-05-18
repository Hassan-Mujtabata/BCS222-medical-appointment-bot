(defn should-submit-form [first-visit specialty payment-method]
  (if (and (= first-visit "Yes")
           (not (= specialty "Other"))
           (or (= payment-method "Self-pay")
               (= payment-method "Insurance")))
    True
    False))
